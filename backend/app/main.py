from fastapi import FastAPI, WebSocket, Depends, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, os, datetime, json
from .db import get_db, init_db
from .llm_adapter import generate_reply
from .auth import require_admin
from .auth_jwt import require_admin_either

app = FastAPI(title="AI Customer Support Bot - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB (simple file-based migration)
init_db()

class CreateSessionResp(BaseModel):
    session_id: str

class MessageIn(BaseModel):
    text: str
    user_id: str | None = None

@app.post("/api/v1/sessions", response_model=CreateSessionResp)
def create_session():
    sid = str(uuid.uuid4())
    db = get_db()
    db.execute("INSERT INTO sessions (id, start_at, last_active_at, status) VALUES (?, ?, ?, ?)",
               (sid, datetime.datetime.utcnow().isoformat(), datetime.datetime.utcnow().isoformat(), "open"))
    db.commit()
    return {"session_id": sid}

@app.get("/api/v1/sessions/{session_id}")
def get_session(session_id: str = Path(...)):
    db = get_db()
    r = db.execute("SELECT id, start_at, last_active_at, status FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="session not found")
    return {"id": r[0], "start_at": r[1], "last_active_at": r[2], "status": r[3]}

@app.post("/api/v1/sessions/{session_id}/message")
def send_message(session_id: str, msg: MessageIn):
    db = get_db()
    s = db.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    now = datetime.datetime.utcnow().isoformat()
    # persist user message
    db.execute("INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
               (session_id, "user", msg.text, now))
    db.commit()
    # retrieve last N messages (simple)
    rows = db.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 8", (session_id,)).fetchall()
    history = [{"role": r[0], "content": r[1]} for r in reversed(rows)]
    # call LLM adapter (dummy or real)
    reply_text, suggested_action, confidence = generate_reply(user_text=msg.text, history=history, db=db)
    db.execute("INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
               (session_id, "assistant", reply_text, now))
    db.commit()
    return {"text": reply_text, "suggested_action": suggested_action, "confidence": confidence}

@app.get("/api/v1/sessions/{session_id}/messages")
def list_messages(session_id: str):
    db = get_db()
    rows = db.execute("SELECT id, session_id, role, content, created_at FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,)).fetchall()
    return [{"id": r[0], "session_id": r[1], "role": r[2], "content": r[3], "created_at": r[4]} for r in rows]

@app.post("/api/v1/sessions/{session_id}/escalate")
def escalate(session_id: str, reason: dict | None = None):
    db = get_db()
    s = db.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    now = datetime.datetime.utcnow().isoformat()
    db.execute("INSERT INTO escalations (session_id, reason, created_at) VALUES (?, ?, ?)",
               (session_id, json.dumps(reason) if reason else "manual_escalation", now))
    db.execute("UPDATE sessions SET status = ? WHERE id = ?", ("escalated", session_id))
    db.commit()
    return {"ok": True, "message": "session escalated"}

@app.post("/api/v1/faqs")
def add_faq(item: dict, admin: bool = Depends(require_admin_either)):
    db = get_db()
    now = datetime.datetime.utcnow().isoformat()
    db.execute("INSERT INTO faqs (title, content, tags, created_at) VALUES (?, ?, ?, ?)",
               (item.get("title","untitled"), item.get("content",""), json.dumps(item.get("tags",[])), now))
    db.commit()
    return {"ok": True}

@app.get("/api/v1/metrics")
def metrics(admin: bool = Depends(require_admin_either)):
    db = get_db()
    total_sessions = db.execute("SELECT COUNT(*) as c FROM sessions").fetchone()[0]
    open_sessions = db.execute("SELECT COUNT(*) as c FROM sessions WHERE status = 'open'").fetchone()[0]
    escalated = db.execute("SELECT COUNT(*) as c FROM escalations").fetchone()[0]
    messages = db.execute("SELECT COUNT(*) as c FROM messages").fetchone()[0]
    faqs = db.execute("SELECT COUNT(*) as c FROM faqs").fetchone()[0]
    return {"total_sessions": total_sessions, "open_sessions": open_sessions, "escalated": escalated, "messages": messages, "faqs": faqs}

@app.post("/api/v1/reindex")
def reindex(admin: bool = Depends(require_admin_either)):
    # simple reindex: for this demo we don't build vector DB, but this endpoint could be used to trigger background reindexing
    return {"ok": True, "message": "reindex (demo) - no-op"}

@app.post("/api/v1/feedback")
def feedback(item: dict):
    db = get_db()
    now = datetime.datetime.utcnow().isoformat()
    db.execute("INSERT INTO feedback (session_id, message_id, rating, comments, created_at) VALUES (?, ?, ?, ?, ?)",
               (item.get("session_id"), item.get("message_id"), item.get("rating"), item.get("comments",""), now))
    db.commit()
    return {"ok": True}
