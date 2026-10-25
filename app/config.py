import os
from dotenv import load_dotenv

load_dotenv()

DOCS_DIR = "data/docs"
ACL_FILE = "data/acl.json"
CHROMA_DIR = "chroma_db"
COLLECTION = "company_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

ROLES = ["employee", "hr", "finance", "admin"]
TOP_K = 4

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-env")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

# Demo users. Passwords are plain for now; we'll hash them later.
USERS = {
    "alice": {"password": "alice123", "role": "employee"},
    "harry": {"password": "harry123", "role": "hr"},
    "frank": {"password": "frank123", "role": "finance"},
    "root":  {"password": "root123",  "role": "admin"},
}

MIN_SIMILARITY = 0.30

JUDGE_MODEL = os.getenv("JUDGE_MODEL", "ministral-3b-latest")
GROUNDEDNESS_ENABLED = os.getenv("GROUNDEDNESS_ENABLED", "true").lower() == "true"
GUARDRAILS_ENABLED = os.getenv("GUARDRAILS_ENABLED", "true").lower() == "true"
ACCESS_CONTROL_ENABLED = os.getenv("ACCESS_CONTROL_ENABLED", "true").lower() == "true"
