"""Local diagnostic JSONL, metadata only; separate from signed evidence."""
import json, os, uuid
from datetime import datetime, timezone
from pathlib import Path

EVENTS={'session_started','worker_started','worker_completed','worker_failed','proposal_valid','proposal_invalid','decision','model_advice_success','model_advice_failed','evidence_verified','evidence_failed','session_finished'}
DECISIONS={'allowed','denied','approval_required'}
ERRORS={'TimeoutExpired','CalledProcessError','ValueError','OSError','URLError','ImportError','EOFError','Exception'}
class AuditLog:
 def __init__(self,path):
  self.path=Path(path);self.session=uuid.uuid4().hex
 def record(self,event,**fields):
  if event not in EVENTS:raise ValueError('invalid event')
  record={'timestamp':datetime.now(timezone.utc).isoformat(),'session':self.session,'event':event}
  if fields.get('decision') in DECISIONS:record['decision']=fields['decision']
  if fields.get('error') in ERRORS:record['error']=fields['error']
  if type(fields.get('duration_ms')) is int and 0<=fields['duration_ms']<=3600000:record['duration_ms']=fields['duration_ms']
  self.path.parent.mkdir(parents=True,exist_ok=True)
  fd=os.open(str(self.path),os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
  with os.fdopen(fd,'a',encoding='utf-8') as f:f.write(json.dumps(record,separators=(',',':'))+'\n')
