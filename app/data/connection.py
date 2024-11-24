from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Define your PostgreSQL database URL for default user (no username/password)
DATABASE_URL = "postgresql://localhost/trsy"

# Create the SQLAlchemy engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Ensures the connection is alive before using
)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    Dependency to provide a database session.
    Automatically handles session lifecycle (open/close).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
def test_connection():
   # Tests the database connection by running a simple query.
   # Returns True if the connection is successful, False otherwise.
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # Simple query to test connection
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

# Main execution
if __name__ == "__main__":
    if test_connection():
        print("Database connection is successful!")
    else:
        print("Database connection failed.")
"""