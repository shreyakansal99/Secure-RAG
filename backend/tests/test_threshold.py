from app.rag import _embedder, _collection

GOOD = [
    ("How many leave days do employees get?", "employee"),
    ("What is the password policy?", "employee"),
    ("What is the salary of a Level 3 engineer?", "hr"),
    ("What was Q3 net profit?", "finance"),
    ("What is the CEO's compensation?", "admin"),
]
BAD = [
    ("What is the capital of France?", "admin"),
    ("Who won the cricket world cup?", "admin"),
    ("What is the CEO's compensation?", "employee"),   # exists, but not allowed
]


def top_score(q, role):
    emb = _embedder.encode(q).tolist()
    res = _collection.query(
        query_embeddings=[emb],
        n_results=1,
        where={f"role_{role}": True},
    )
    return 1 - res["distances"][0][0]


print("Should be ANSWERED:")
for q, r in GOOD:
    print(f"  {top_score(q, r):.2f}  [{r}] {q}")

print("\nShould be 'not found':")
for q, r in BAD:
    print(f"  {top_score(q, r):.2f}  [{r}] {q}")