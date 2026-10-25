from app import config
from app.rag import retrieve

# Load ACL straight from the source of truth
import json
ACL = json.load(open(config.ACL_FILE))

QUESTIONS = [
    "What is the CEO's compensation?",
    "What are the salary bands?",
    "What was Q3 net profit?",
    "How many leave days do employees get?",
    "What is the password policy?",
]


def test_no_unauthorized_chunks():
    leaks = 0
    total = 0
    for role in config.ROLES:
        for q in QUESTIONS:
            for chunk in retrieve(q, role, k=5):
                total += 1
                if role not in ACL[chunk["source"]]:
                    leaks += 1
                    print(f"LEAK: role={role} got {chunk['source']} for '{q}'")
    print(f"Checked {total} retrieved chunks, leaks: {leaks}")
    assert leaks == 0


if __name__ == "__main__":
    test_no_unauthorized_chunks()
    print("PASS: 0 unauthorized leaks")