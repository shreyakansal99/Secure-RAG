from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app import config
from app.rag import answer
import time
from app.audit import log_request
from fastapi.middleware.cors import CORSMiddleware  
from app import history

app = FastAPI(title="Secure RAG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
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


@app.get("/me")
def me(user=Depends(current_user)):
    return user


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
    a = result["answer"]
    if (not result.get("blocked") and result.get("sources")
            and not a.startswith(("[LLM error", "I couldn't", "I can't"))):
        history.save(user["username"], user["role"], result["redacted_query"],
                     a, [{"source": s["source"], "page": s["page"]} for s in result["sources"]])
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


@app.get("/history")
def get_history(q: str = "", user=Depends(current_user)):
    return history.search(user["username"], user["role"], q)


@app.delete("/history/{item_id}")
def delete_history_item(item_id: int, user=Depends(current_user)):
    history.delete(user["username"], item_id)
    return {"ok": True}


@app.delete("/history")
def clear_history(user=Depends(current_user)):
    history.clear(user["username"])
    return {"ok": True}