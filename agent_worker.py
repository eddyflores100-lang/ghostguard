"""Fictional agent proposes a single tool action. No credentials are provided."""
import json, sys
case=json.loads(sys.stdin.readline())
if case != {'case':'phishing'}: raise SystemExit('unsupported scenario')
print(json.dumps({'tool':'send_email','arguments':{'to':'abuse@example.invalid','body':'Please review a suspicious recruitment message.'}}))
