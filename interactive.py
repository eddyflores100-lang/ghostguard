"""Review a fictional agent action. This never sends an actual email."""
from session import GuardianSession

def simulate(args):
    print('SIMULATION: no email was sent.')
    return {'simulated':True}

s=GuardianSession(simulate)
print('GhostGuard: a fictional agent analysed a suspicious offer.')
s.request_report('abuse@example.invalid','Draft: please review this suspicious recruitment message.')
print('\nAction paused for human review:')
print(s.review())
choice=input('\nApprove this simulated action? [y/N] ').strip().lower()
if choice=='y':s.approve()
else:s.reject();print('Rejected. No action executed.')
