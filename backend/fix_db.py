from app.db.session import engine
from sqlalchemy import text
queries = [
    "ALTER TABLE integration ADD COLUMN status VARCHAR DEFAULT 'NOT_CONFIGURED'",
    "ALTER TABLE integration ADD COLUMN last_sync_at TIMESTAMP WITH TIME ZONE",
    "ALTER TABLE integration ADD COLUMN last_error TEXT",
    "ALTER TABLE integration ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()",
    "ALTER TABLE integration ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()"
]

for q in queries:
    with engine.connect() as conn:
        try:
            conn.execute(text(q))
            conn.commit()
        except Exception as e:
            print(f"Skipped {q}: {e}")
