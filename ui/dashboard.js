'use strict';
const launchToken = location.hash.slice(1);
if (launchToken) sessionStorage.setItem('ghostguard-token', launchToken);
const token = launchToken || sessionStorage.getItem('ghostguard-token') || '';
history.replaceState(null, '', '/');
const el = id => document.getElementById(id);
let busy = false;
async function call(path, data) {
  if (!token) throw new Error('This tab has no session token. Open the private URL printed by GhostGuard.');
  const r = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json','X-GhostGuard-Token':token}, body:JSON.stringify(data)});
  const j = await r.json(); if (!r.ok) throw new Error(j.error || 'Request failed'); return j;
}
function setBusy(value) {busy=value; for(const id of ['start','approve','reject']) el(id).disabled=value;}
function showProposal(p) {
  for(const key of ['tool','recipient','draft','advice']) el(key).textContent=p[key];
  el('review').hidden=false;el('empty').hidden=true;el('state').textContent='AWAITING YOUR REVIEW';
  el('message').textContent='This action is paused. Nothing has been sent.';
}
if (token) call('/api/status',{}).then(p=>{if(p.decision==='approval_required')showProposal(p);}).catch(e=>{el('message').textContent=e.message;});
el('start').onclick = async () => {
  if (busy) return; setBusy(true); el('message').textContent='Generating with your local model…';
  try { const p=await call('/api/propose',{}); showProposal(p); }
  catch(e) {el('message').textContent=e.message;} finally {setBusy(false);}
};
for (const decision of ['approve','reject']) el(decision).onclick=async()=>{
  if(busy)return;setBusy(true);
  try {const r=await call('/api/decide',{decision});el('review').hidden=true;el('empty').hidden=false;el('state').textContent=r.decision.toUpperCase();el('message').textContent=r.simulated?'Approved simulation. No email was sent.':'Rejected or expired. No action was executed.';if(r.evidence_verified)el('message').textContent+=' Signed evidence verified.';}
  catch(e){el('message').textContent=e.message;}finally{setBusy(false);}
};
