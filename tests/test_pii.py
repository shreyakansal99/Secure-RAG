from app.guardrails.pii import redact

CASES = [
    "My email is rahul@gmail.com",
    "Call me on 98765 43210",
    "Phone +91 98765 43210 please",
    "My Aadhaar is 2345 6789 0123",
    "My PAN is ABCDE1234F",
    "Card 4111 1111 1111 1111",
    "How many leave days do employees get?",       # should stay unchanged
    "What is the salary of a Level 3 engineer?",   # should stay unchanged
]

for text in CASES:
    out, found = redact(text)
    print(f"{text!r}\n  -> {out!r}  {found}\n")