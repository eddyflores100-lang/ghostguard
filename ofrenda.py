"""The Ofrenda: a terminal vigil honoring the incidents that shaped GhostGuard.

This challenge ran across Halloween and Dia de los Muertos (Nov 1-2). In that
spirit, the ofrenda is not decoration: every candle is a lesson drawn from a
real, documented incident, and every lesson names the guard mechanism that
enforces it today. `--check` fails closed if that mapping breaks, and the
test suite verifies it against the living code.

Pure ASCII, standard library only, no network access.
"""
import argparse
import json
import sys
from pathlib import Path

DEFAULT_DATA = Path(__file__).resolve().parent / "data" / "incidents.json"
WIDTH = 68

REQUIRED_FIELDS = ("id", "name", "first_seen", "laid_to_rest", "epitaph")
LESSON_FIELDS = ("candle", "lesson", "enforced_by")

# Where each honored lesson actually lives in the code, today. If a mechanism
# is removed from the code, --check and the tests fail; the vigil is a contract.
ENFORCED = {
    "allowlist": "Guard.run executes only allowlisted demo tools; everything else is denied",
    "human_approval": "external actions pause as approval_required until a person decides",
    "approval_ttl": "approval capabilities expire (default 300s) and expired ones cannot execute",
    "digest_binding": "a token is single-use and bound to the SHA-256 digest of the exact tool and arguments",
    "simulated_effect": "every external effect in this project is simulated; no email is sent",
    "signed_evidence": "optional Alethech adapter signs decision metadata and verifies the store",
    "advisory_only_model": "the local model receives only tool/decision labels and never changes policy",
}


def load_incidents(path=DEFAULT_DATA):
    """Load and validate the incident data; raise ValueError on any gap."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read incidents: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("incidents"), list) or not raw["incidents"]:
        raise ValueError("incidents must be a non-empty list")
    for incident in raw["incidents"]:
        for field in REQUIRED_FIELDS:
            if not isinstance(incident.get(field), str) or not incident.get(field):
                raise ValueError(f"incident missing field: {field}")
        if not incident["lessons"]:
            raise ValueError("incident must carry at least one lesson")
        for lesson in incident["lessons"]:
            for field in LESSON_FIELDS:
                if not isinstance(lesson.get(field), str) or not lesson.get(field):
                    raise ValueError(f"lesson missing field: {field}")
    return raw["incidents"]


def _center(text, width=WIDTH):
    return text.center(width)


def render(incidents):
    """Return the ASCII ofrenda as a single string."""
    out = []
    out.append("." + "=" * (WIDTH - 2) + ".")
    out.append("|" + _center("T H E   O F R E N D A", WIDTH - 2) + "|")
    out.append("|" + _center("a vigil for the incidents that shaped GhostGuard", WIDTH - 2) + "|")
    out.append("'" + "=" * (WIDTH - 2) + "'")
    out.append("")
    out.append(_center("Dia de los Muertos, 2026. They are remembered. They teach."))
    out.append("")

    for incident in incidents:
        out.append(_center(".---------------------------."))
        out.append(_center("|       IN MEMORIAM         |"))
        out.append(_center("|                           |"))
        for line in _wrap(incident["name"], 25):
            out.append(_center(f"| {line:<25} |"))
        out.append(_center("|                           |"))
        out.append(_center(f"| born           {incident['first_seen']:<10} |"))
        out.append(_center(f"| laid to rest   {incident['laid_to_rest']:<10} |"))
        if incident.get("rest_verified"):
            out.append(_center(f"| rest verified  {incident['rest_verified']:<10} |"))
        out.append(_center("|                           |"))
        out.append(_center("'---------------------------'"))
        out.append("")
        for line in _wrap(f'"{incident["epitaph"]}"', WIDTH - 8):
            out.append(_center(line))
        if incident.get("evidence"):
            out.append("")
            out.append(_center("Evidence:"))
            for line in _wrap(incident["evidence"], WIDTH - 10):
                out.append(_center(line))
        out.append("")

        lessons = incident["lessons"]
        out.append(f"  {len(lessons)} CANDLES -- one for each lesson the guard now enforces")
        out.append("")
        row_a = "    " + "  ".join("( )" for _ in lessons)
        row_b = "    " + "  ".join(")|(" for _ in lessons)
        row_c = "    " + "  ".join("(__)" for _ in lessons)
        out.append(row_a)
        out.append(row_b)
        out.append(row_c)
        out.append("")
        for number, lesson in enumerate(lessons, start=1):
            out.append(f"    {number}. {lesson['candle']}")
            for line in _wrap(lesson["lesson"], WIDTH - 12):
                out.append(f"        {line}")
            out.append(f"        -> enforced by {lesson['enforced_by']}")
            out.append("")
    out.append("  OFFERINGS -- mechanisms that are in the code today, not wishes")
    out.append("")
    for name, where in ENFORCED.items():
        lines = _wrap(where, WIDTH - 28)
        out.append(f"    {name:<20} {lines[0]}")
        for extra in lines[1:]:
            out.append(f"    {'':<20} {extra}")
    out.append("")
    out.append(_center("~ * ~  cempasuchil: may the living find the way home  ~ * ~"))
    out.append("")
    return "\n".join(out)


def _wrap(text, width):
    words, lines, current = text.split(), [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines


def check(incidents):
    """Fail closed: every lesson must map to a real mechanism, and every
    mechanism must be honored by at least one lesson."""
    problems = []
    honored = set()
    for incident in incidents:
        for lesson in incident["lessons"]:
            mechanism = lesson["enforced_by"]
            if mechanism not in ENFORCED:
                problems.append(f"{incident['id']}: lesson '{lesson['candle']}' maps to unknown mechanism '{mechanism}'")
            else:
                honored.add(mechanism)
    for mechanism in ENFORCED:
        if mechanism not in honored:
            problems.append(f"mechanism '{mechanism}' is enforced in code but honored by no candle")
    return problems


def main():
    parser = argparse.ArgumentParser(description="Render the GhostGuard ofrenda")
    parser.add_argument("--file", default=str(DEFAULT_DATA), help="path to incidents JSON")
    parser.add_argument("--json", action="store_true", help="print machine-readable incidents and mechanisms")
    parser.add_argument("--check", action="store_true", help="verify the lesson-to-mechanism mapping and exit")
    args = parser.parse_args()
    try:
        incidents = load_incidents(args.file)
    except ValueError as exc:
        print(f"ofrenda: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if args.check:
        problems = check(incidents)
        for problem in problems:
            print(f"ofrenda check: {problem}", file=sys.stderr)
        if problems:
            raise SystemExit(1)
        print("ofrenda check: every candle maps to an enforced mechanism; every mechanism is honored.")
        return
    if args.json:
        print(json.dumps({"incidents": incidents, "enforced": ENFORCED}, indent=2))
        return
    print(render(incidents))


if __name__ == "__main__":
    main()
