# create_dummy_data.py

import os
import pymysql

def create_and_populate_db_and_table():
    # 1. Connect to MySQL *without* specifying a database initially
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "fill in your password here"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    db_name = os.getenv("MYSQL_DB", "mentee_db")  # default DB name if none specified
    try:
        with connection.cursor() as cursor:
            # 2. Create the database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")

        # 3. Switch to the newly created or existing database
        connection.select_db(db_name)

        with connection.cursor() as cursor:
            # 4. Create the mentees table if it does not exist
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS mentees (
                id INT NOT NULL AUTO_INCREMENT,
                background VARCHAR(255),
                experience TEXT,
                learning_style VARCHAR(255),
                availability VARCHAR(255),
                personality VARCHAR(255),
                unit_needs VARCHAR(255),
                PRIMARY KEY (id)
            );
            """
            cursor.execute(create_table_sql)

            # 5. Insert dummy records
            insert_data_sql = """
            INSERT INTO mentees
                (background, experience, learning_style, availability, personality, unit_needs)
            VALUES
                (%s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_data_sql, (
                # Mentee #1
                "New grad nurse with a passion for community healthcare",
                "6-month internship at a local clinic",
                "Hands-on and visual learning",
                "Weekdays, day shifts",
                "Friendly and proactive",
                "Community / Public Health",
                # Mentee #2
                "2 years in med-surg, looking to move into critical care",
                "Basic knowledge of ICU protocols",
                "Structured and theory-based learning",
                "Weekends, flexible schedules",
                "Calm under pressure",
                "Critical Care / ICU",
                # Mentee #3
                "Recent graduate from an accelerated BSN program",
                "Previous work as an EMT",
                "Interactive and simulation-based learning",
                "Night shifts only",
                "Adaptable and curious",
                "Emergency Nursing"
            ))

        connection.commit()
    finally:
        connection.close()

if __name__ == "__main__":
    create_and_populate_db_and_table()
    print("Database, table, and dummy data created successfully!")
