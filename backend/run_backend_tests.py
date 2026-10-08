import os
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def reset_test_db():
    print("Connecting to postgres to reset test database...")
    # Connect to the default 'postgres' database
    conn = psycopg2.connect(
        user="standbharat_user",
        password="standbharat_password",
        host="localhost",
        port="5432",
        dbname="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Drop and recreate the test database
    cursor.execute("DROP DATABASE IF EXISTS standbharat_test_db")
    cursor.execute("CREATE DATABASE standbharat_test_db")
    
    cursor.close()
    conn.close()
    print("Test database recreated.")

def run_migrations():
    print("Running migrations on test database...")
    env = os.environ.copy()
    env["POSTGRES_DB"] = "standbharat_test_db"
    subprocess.run(["alembic", "upgrade", "head"], env=env, check=True)
    print("Migrations complete.")

def run_tests():
    print("Running pytest...")
    env = os.environ.copy()
    env["POSTGRES_DB"] = "standbharat_test_db"
    env["PYTHONPATH"] = "."
    result = subprocess.run(["pytest", "tests/", "-v"], env=env)
    return result.returncode

if __name__ == "__main__":
    reset_test_db()
    run_migrations()
    exit_code = run_tests()
    exit(exit_code)
