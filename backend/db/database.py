import psycopg2
from psycopg2.extras import DictCursor

# Database configuration
DB_CONFIG = {
    "dbname": "finisher_db",
    "user": "your_username",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def connect_db():
    """Establishes connection to PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_tables():
    """Creates database tables for users, lyrics, and AI feedback."""
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE,
                        email VARCHAR(100) UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS lyrics (
                        id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(id),
                        text TEXT,
                        mood VARCHAR(50),
                        genre VARCHAR(50),
                        bpm INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS ai_feedback (
                        id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(id),
                        lyric_id INT REFERENCES lyrics(id),
                        rating INT CHECK (rating BETWEEN 1 AND 5),
                        user_edits TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                print("✅ Tables created successfully!")
        except Exception as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()

# Run the function to set up the database
if __name__ == "__main__":
    create_tables()
