"""Bounded local read-only jobs. No model, shell, network or write tools."""
import argparse
import json
import sqlite3
from pathlib import Path

class Runtime:
    def __init__(self, database, workspace):
        self.root = Path(workspace).resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError('Workspace must be a directory')
        self.db = sqlite3.connect(database)
        self.db.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, path TEXT, state TEXT, result TEXT)')
        # Interrupted reads are never silently replayed.
        self.db.execute("UPDATE jobs SET state='interrupted' WHERE state='running'")
        self.db.commit()

    def submit(self, path):
        p = Path(path)
        if p.is_absolute() or not p.parts or any(x in ('.', '..') or x.startswith('.') for x in p.parts):
            raise ValueError('Use a non-hidden relative file path')
        cur = self.db.execute("INSERT INTO jobs(path,state) VALUES (?, 'queued')", (str(p),))
        self.db.commit()
        return cur.lastrowid

    def cancel(self, job):
        cur = self.db.execute("UPDATE jobs SET state='cancelled' WHERE id=? AND state='queued'", (job,))
        self.db.commit()
        return cur.rowcount == 1

    def run(self, limit=5, max_bytes=65536):
        if not 1 <= limit <= 20 or not 1 <= max_bytes <= 1048576:
            raise ValueError('Invalid execution budget')
        done = []
        for _ in range(limit):
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute("SELECT id,path FROM jobs WHERE state='queued' ORDER BY id LIMIT 1").fetchone()
            if not row:
                self.db.commit()
                break
            job, name = row
            self.db.execute("UPDATE jobs SET state='running' WHERE id=?", (job,))
            self.db.commit()
            try:
                path = self.root
                for component in Path(name).parts:
                    path = path / component
                    if path.is_symlink():
                        raise ValueError('Symlinks are not supported')
                resolved = path.resolve(strict=True)
                resolved.relative_to(self.root)
                if not resolved.is_file():
                    raise ValueError('Regular file required')
                with resolved.open('rb') as stream:
                    data = stream.read(max_bytes + 1)
                if len(data) > max_bytes:
                    raise ValueError('File exceeds budget')
                text = data.decode('utf-8')
                # Persist metadata only, never file contents.
                result = json.dumps({'bytes': len(data), 'lines': len(text.splitlines())})
                state = 'completed'
            except (OSError, UnicodeError, ValueError):
                state, result = 'failed', json.dumps({'error': 'File unavailable or outside read policy'})
            self.db.execute('UPDATE jobs SET state=?,result=? WHERE id=?', (state, result, job))
            self.db.commit()
            done.append(job)
        return done

    def status(self):
        return self.db.execute('SELECT id,state,result FROM jobs ORDER BY id').fetchall()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--database', required=True)
    p.add_argument('--workspace', required=True)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('submit').add_argument('path')
    sub.add_parser('cancel').add_argument('job', type=int)
    sub.add_parser('run').add_argument('--limit', type=int, default=5)
    sub.add_parser('status')
    args = p.parse_args()
    runtime = Runtime(args.database, args.workspace)
    try:
        if args.command == 'submit': result = runtime.submit(args.path)
        elif args.command == 'cancel': result = runtime.cancel(args.job)
        elif args.command == 'run': result = runtime.run(args.limit)
        else: result = runtime.status()
        print(json.dumps(result))
    finally:
        runtime.db.close()

if __name__ == '__main__':
    main()
