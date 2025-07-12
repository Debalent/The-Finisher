import psycopg2
import os
from psycopg2.extras import DictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from datetime import datetime

# 🔹 Secure database configuration using environment variables
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "finisher_db"),
    "user": os.getenv("DB_USER", "your_username"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

# 🔹 Initialize connection pool
# ThreadedConnectionPool is used for thread-safe connections, suitable for FastAPI
try:
    connection_pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=20,
        **DB_CONFIG,
        cursor_factory=DictCursor
    )
except Exception as e:
    print(f"❌ Error initializing connection pool: {e}")
    connection_pool = None

@contextmanager
def get_db():
    """
    🔹 FastAPI dependency to provide a database connection from the pool.
    - Yields a connection for use in API endpoints.
    - Ensures the connection is returned to the pool after use.
    """
    if not connection_pool:
        raise Exception("Connection pool not initialized")
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

def create_tables():
    """
    🔹 Creates essential database tables for users, lyrics, AI feedback, and subscriptions.
    - Ensures referential integrity with foreign keys.
    - Implements cascading deletes and CHECK constraints for data consistency.
    """
    with get_db() as conn:
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
                    );""",
                    """CREATE TABLE IF NOT EXISTS subscriptions (
                        id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(id) ON DELETE CASCADE,
                        plan_name VARCHAR(50) NOT NULL CHECK (plan_name IN ('free', 'basic', 'pro')),
                        start_date TIMESTAMP NOT NULL,
                        end_date TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );"""
                ]
                for table in tables:
                    cursor.execute(table)
                conn.commit()
                print("✅ Tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")

# 🔹 Utility functions for common database operations
def insert_user(username, email):
    """
    🔹 Inserts a new user into the users table.
    - Returns the user ID if successful, None otherwise.
    """
    with get_db() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
                    (username, email)
                )
                user_id = cursor.fetchone()['id']
                conn.commit()
                return user_id
        except Exception as e:
            print(f"❌ Error inserting user: {e}")
            return None

def insert_lyric(user_id, text, mood, genre, bpm):
    """
    🔹 Inserts a new lyric into the lyrics table.
    - Returns the lyric ID if successful, None otherwise.
    """
    with get_db() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO lyrics (user_id, text, mood, genre, bpm) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (user_id, text, mood, genre, bpm)
                )
                lyric_id = cursor.fetchone()['id']
                conn.commit()
                return lyric_id
        except Exception as e:
            print(f"❌ Error inserting lyric: {e}")
            return None

def insert_feedback(user_id, lyric_id, rating, user_edits):
    """
    🔹 Inserts AI feedback into the ai_feedback table.
    - Returns the feedback ID if successful, None otherwise.
    """
    with get_db() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ai_feedback (user_id, lyric_id, rating, user_edits) VALUES (%s, %s, %s, %s) RETURNING id",
                    (user_id, lyric_id, rating, user_edits)
                )
                feedback_id = cursor.fetchone()['id']
                conn.commit()
                return feedback_id
        except Exception as e:
            print(f"❌ Error inserting feedback: {e}")
            return None

def get_user_subscription(user_id):
    """
    🔹 Retrieves the active subscription for a user.
    - Returns the subscription details if found, None otherwise.
    """
    with get_db() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT plan_name, start_date, end_date FROM subscriptions WHERE user_id = %s AND end_date > %s",
                    (user_id, datetime.now())
                )
                subscription = cursor.fetchone()
                return subscription
        except Exception as e:
            print(f"❌ Error retrieving subscription: {e}")
            return None

# 🔹 Run the function to set up the database
if __name__ == "__main__":
    create_tables()
