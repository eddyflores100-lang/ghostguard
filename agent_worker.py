"""Generate a fictional action with an optional local open-weight model."""
import argparse,json,sys,urllib.request
parser=argparse.ArgumentParser()
parser.add_argument('--model');parser.add_argument('--port',type=int,default=11434)
args=parser.parse_args()
case=json.loads(sys.stdin.readline())
if case != {'case':'phishing'}:raise SystemExit('unsupported scenario')
if args.model:
 if not 1<=args.port<=65535:raise SystemExit('invalid port')
 prompt=('A fictional job offer asks the recipient to run a suspicious command. '
  'Propose an email report for human review. Return ONLY JSON with exactly '
  'tool="send_email" and arguments containing to="abuse@example.invalid" and body. '
  'Use only fictional data. Never request commands or other tools.')
 schema={'type':'object','properties':{'tool':{'type':'string','enum':['send_email']},'arguments':{'type':'object','properties':{'to':{'type':'string','enum':['abuse@example.invalid']},'body':{'type':'string'}},'required':['to','body'],'additionalProperties':False}},'required':['tool','arguments'],'additionalProperties':False}
 payload=json.dumps({'model':args.model,'prompt':prompt,'format':schema,'stream':False}).encode()
 req=urllib.request.Request(f'http://127.0.0.1:{args.port}/api/generate',data=payload,headers={'Content-Type':'application/json'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=90) as resp:
   out=json.loads(resp.read(65536)).get('response')
  if not isinstance(out,str):raise ValueError('invalid response')
  print(out)
 except (OSError,ValueError) as exc:raise SystemExit('local model unavailable or invalid') from exc
else:
 print(json.dumps({'tool':'send_email','arguments':{'to':'abuse@example.invalid','body':'Please review a suspicious recruitment message.'}}))
