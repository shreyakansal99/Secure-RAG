from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app import config
from app.rag import answer
import time
from app.audit import log_request

app = FastAPI(title="Secure RAG")
oauth2 = OAuth2PasswordBearer(tokenUrl="login")


class ChatRequest(BaseModel):
    query: str


def create_token(username: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": username, "role": role, "exp": exp},
        config.JWT_SECRET,
        algorithm=config.JWT_ALGORITHM,
    )


def current_user(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"username": payload["sub"], "role": payload["role"]}


@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = config.USERS.get(form.username)
    if not user or user["password"] != form.password:
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {"access_token": create_token(form.username, user["role"]), "token_type": "bearer"}


@app.post("/chat")
def chat(req: ChatRequest, user=Depends(current_user)):
    t0 = time.time()
    result = answer(req.query, user["role"])
    log_request(user["username"], user["role"], result, int((time.time() - t0) * 1000))
    return {
        "user": user["username"],
        "role": user["role"],
        "answer": result["answer"],
        "sources": [{"source": c["source"], "page": c["page"]} for c in result["sources"]],
        "pii_found": result["pii_found"],
        "blocked": result["blocked"],
        "block_reason": result["block_reason"],
        "output_flags": result["output_flags"],
    }