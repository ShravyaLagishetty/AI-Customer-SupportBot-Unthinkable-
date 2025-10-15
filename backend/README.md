Backend API Quick Reference

Run: `uvicorn app.main:app --reload --port 8000`

Core endpoints:
- POST /api/v1/sessions                 -> create session
- GET  /api/v1/sessions/{session_id}    -> get session meta
- POST /api/v1/sessions/{id}/message    -> send user message
- GET  /api/v1/sessions/{id}/messages   -> list messages
- POST /api/v1/sessions/{id}/escalate   -> escalate to human
- POST /api/v1/faqs                     -> add FAQ (admin) (supports x-api-key or Bearer JWT)
- POST /api/v1/reindex                  -> reindex (admin) - triggers demo reindex
- GET  /api/v1/metrics                  -> metrics (admin)
- POST /api/v1/feedback                 -> submit feedback

Auth:
- Admin endpoints accept either header `x-api-key: <ADMIN_API_KEY>` or `Authorization: Bearer <JWT>`.
- Use `backend/app/auth_jwt.create_jwt({'role':'admin','sub':'user'})` to generate a demo admin JWT (requires PyJWT).

LLM:
- The llm_adapter will call OpenAI if OPENAI_API_KEY is set, otherwise uses deterministic fallback.

Celery:
- Worker configured in `worker.py`. Start with:
  `docker-compose up --build` (worker service will run celery)
  or to run locally:
  `celery -A worker.cel worker --loglevel=info` (requires redis)

Tests:
- `pytest` in backend will run simple integration tests using TestClient.

