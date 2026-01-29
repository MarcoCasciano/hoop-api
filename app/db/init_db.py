from app.db.database import engine
from app.db.models import Base  # importa Brew indirettamente

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("✅ DB e tabelle creati")
