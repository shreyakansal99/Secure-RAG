import time
from app.guardrails.output import check_groundedness

CONTEXT = [{"text": "All full-time employees receive 24 days of paid annual leave per year. "
                    "Sick leave: 12 days per year."}]

CASES = [
    ("Employees get 24 days of annual leave [leave_policy.txt].", True),
    ("Employees get 30 days of annual leave [leave_policy.txt].", False),   # wrong number
    ("Employees get 24 days of leave and free lunch [leave_policy.txt].", False),  # invented
    ("Sick leave is 12 days per year [leave_policy.txt].", True),
]

for ans, expected in CASES:
    ok, reason = check_groundedness(ans, CONTEXT)
    print(f"{'OK  ' if ok == expected else 'WRONG'} expected={expected} got={ok} | {ans}\n      reason: {reason}")
    time.sleep(1.5)   # respect 1 request/second