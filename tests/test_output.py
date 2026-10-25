from app.guardrails.output import check_output

ALLOWED = {"leave_policy.txt"}

CASES = [
    ("Employees get 24 days [leave_policy.txt].", "should pass unchanged"),
    ("The CEO earns 4.2 crore [exec_compensation.txt].", "should block: invalid citation"),
    ("Contact rahul@gmail.com for leave [leave_policy.txt].", "should mask email"),
    ("Use key AIzaSyA1234567890abcdefghijklmnopqrstuvw to log in.", "should block: secret"),
]

for text, expect in CASES:
    out, flags = check_output(text, ALLOWED)
    print(f"{expect}\n  in : {text}\n  out: {out}\n  flags: {flags}\n")