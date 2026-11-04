# Local read-only runtime (experimental)

`runtime.py` adds a persistent SQLite queue for explicitly selected UTF-8 files. It autonomously drains a bounded number of jobs and records byte/line counts, not file content. It does not invoke Gemma, send messages or execute shell commands. The existing model/dashboard demonstrations remain separate.

Use a dedicated workspace containing only files authorized for processing, and put the database in a private directory outside it. Run exactly one runtime process per database; startup marks unfinished jobs interrupted. This is recovery bookkeeping, not a multi-worker scheduler. Do not point it at home directories or secret stores. Path checks are not an OS sandbox and do not protect against concurrent filesystem modification by a hostile local process.

```sh
python3 runtime.py --database /private/jobs.sqlite --workspace /approved/files submit report.txt
python3 runtime.py --database /private/jobs.sqlite --workspace /approved/files run --limit 5
python3 runtime.py --database /private/jobs.sqlite --workspace /approved/files status
python3 runtime.py --database /private/jobs.sqlite --workspace /approved/files cancel 2
```

On Windows use the configured Python interpreter and native paths. No packages or paid services are required for this runtime. The execution limit is 1–20 jobs, with 64 KiB per file by default. Hidden paths, parent traversal, symlinks and oversized files are refused. Cancellation applies to queued jobs, not an active read. The database is not encrypted or signed; protect its directory permissions. It is not an Alethech evidence store.

Before remote deployment, operator authentication, database lifecycle/locking, stronger file isolation, secret handling and integration with the guarded model workflow still need implementation and adversarial verification. Do not expose the existing loopback dashboard publicly. Human review remains pending under manual-human-validation.md.
