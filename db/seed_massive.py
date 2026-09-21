import os
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/datasleuth")
fake = Faker()

def generate_massive_data():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 1. Truncate tables for a clean slate
        print("Truncating tables...")
        cursor.execute("TRUNCATE TABLE orders CASCADE;")
        cursor.execute("TRUNCATE TABLE users CASCADE;")
        
        # 2. Generate 5,000 Users
        print("Generating 5,000 users...")
        users = []
        user_emails = set()
        while len(users) < 5000:
            name = fake.name()
            email = fake.email()
            if email not in user_emails:
                user_emails.add(email)
                # Random signup date between Jan 2024 and Dec 2025
                start_date = datetime(2024, 1, 1)
                random_days = random.randint(0, 730)
                signup_date = start_date + timedelta(days=random_days)
                users.append((name, email, signup_date.strftime('%Y-%m-%d')))
                
        execute_values(
            cursor,
            "INSERT INTO users (name, email, signup_date) VALUES %s",
            users
        )
        print("Successfully inserted 5,000 users!")
        
        # We need the inserted IDs to map to orders
        cursor.execute("SELECT id FROM users;")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        # 3. Generate 25,000 Orders
        print("Generating 25,000 orders...")
        orders = []
        statuses = ['completed', 'completed', 'completed', 'pending', 'refunded', 'failed']
        
        for _ in range(25000):
            user_id = random.choice(user_ids)
            amount = round(random.uniform(10.0, 2000.0), 2)
            status = random.choice(statuses)
            # Random order date in 2025 or 2026
            start_date = datetime(2025, 1, 1)
            random_days = random.randint(0, 500)
            order_date = start_date + timedelta(days=random_days)
            orders.append((user_id, amount, status, order_date.strftime('%Y-%m-%d')))
            
        execute_values(
            cursor,
            "INSERT INTO orders (user_id, amount, status, order_date) VALUES %s",
            orders
        )
        print("Successfully inserted 25,000 orders!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error generating data: {e}")

if __name__ == "__main__":
    generate_massive_data()
