"""Strict boundary for a model-generated, simulated email proposal."""
import json
from ghostguard import Action

def parse_proposal(text):
    try:
        if not isinstance(text,str) or len(text)>10000: raise ValueError('proposal size')
        obj=json.loads(text)
        if not isinstance(obj,dict) or set(obj)!={'tool','arguments'} or obj['tool']!='send_email': raise ValueError('tool denied')
        args=obj['arguments']
        if not isinstance(args,dict) or set(args)!={'to','body'}: raise ValueError('invalid fields')
        recipient,body=args['to'],args['body']
        if not isinstance(recipient,str) or not recipient.endswith('@example.invalid') or any(c in recipient for c in '\r\n') or len(recipient)>254: raise ValueError('only simulated recipient accepted')
        if not isinstance(body,str) or not body.strip() or len(body)>4000: raise ValueError('invalid body')
        return Action('send_email',{'to':recipient,'body':body})
    except (json.JSONDecodeError,TypeError,KeyError) as exc: raise ValueError('invalid proposal') from exc
