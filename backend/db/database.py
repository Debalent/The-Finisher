import psycopg2
import os
from psycopg2.extras import DictCursor

# 🔹 Secure database configuration using environment variables
# This ensures sensitive credentials are not hardcoded, improving security.
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "finisher_db"),
    "user": os.getenv("DB_USER", "your_username"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

def connect_db():
    """
    🔹 Establishes a connection to the PostgreSQL database.
    - Uses environment variables for security.
    - Implements DictCursor for optimized query handling.
    - Returns a connection object for further operations.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=DictCursor)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def create_tables():
    """
    🔹 Creates essential database tables for users, lyrics, and AI feedback.
    - Ensures referential integrity with foreign keys.
    - Implements cascading deletes to maintain data consistency.
    - Uses CHECK constraints for data validation.
    """
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                tables = [
                    """CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );""",
                    """CREATE TABLE IF NOT EXISTS lyrics (
                        id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(id) ON DELETE CASCADE,
                        text TEXT NOT NULL,
                        mood VARCHAR(50),
                        genre VARCHAR(50),
                        bpm INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );""",
                    """CREATE TABLE IF NOT EXISTS ai_feedback (
                        id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(id) ON DELETE CASCADE,
                        lyric_id INT REFERENCES lyrics(id) ON DELETE CASCADE,
                        rating INT CHECK (rating BETWEEN 1 AND 5),
                        user_edits TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );"""
                ]
                for table in tables:
                    cursor.execute(table)
                conn.commit()
                print("✅ Tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
        finally:
            conn.close()

# 🔹 Run the function to set up the database
# This ensures the database schema is initialized before usage.
if __name__ == "__main__":
    create_tables()
