import os
from celery import Celery
from app.db import get_db
from time import sleep

CELERY_BROKER = os.environ.get('CELERY_BROKER', 'redis://localhost:6379/0')
cel = Celery('worker', broker=CELERY_BROKER)

@cel.task
def reindex_faqs():
    # demo task: pretend to reindex FAQs into a vector DB
    db = get_db()
    rows = db.execute('SELECT id, title FROM faqs').fetchall()
    # pretend work
    for r in rows:
        print('Indexing FAQ', r[0], r[1][:40])
    return {'count': len(rows)}

@cel.task
def summarize_session(session_id):
    # demo summarization: reads messages and returns a simple summary string (stub)
    db = get_db()
    rows = db.execute('SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,)).fetchall()
    texts = [r[1] for r in rows]
    s = ' '.join(texts)[:1000]
    summary = s[:300] + ('...' if len(s)>300 else '')
    # store summary as a new FAQ-like entry for retrieval demo (optional)
    db.execute('INSERT INTO faqs (title, content, tags, created_at) VALUES (?,?,?,?)', (f'Summary for {session_id}', summary, '[]', 'manual'))
    db.commit()
    return {'summary': summary}
