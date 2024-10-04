import psycopg2
from psycopg2 import sql

def create_table():
    conn_param = {
        'dbname': "your database name",
        'user' : "user name",
        'password' : "your password",
        'host' : "localhost",
        'port': '5432'
    }

    create_book_table_query = '''
        CREATE TABLE books(
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            genre VARCHAR(100),
            year_published INT,
            summary VARCHAR(255)
        )
        '''
    create_review_table_query = '''
        CREATE TABLE reviews(
            id SERIAL PRIMARY KEY,
            FOREIGN KEY (book_id) REFERENCES books(id),
            user_id INT,
            review_text VARCHAR(255) NOT NULL,
            rating INT
        )
       '''
    try:
        conn = psycopg2.connect(**conn_param)
        cur = conn.cursor()
        cur.execute(create_book_table_query)
        cur.execute(create_review_table_query)

        cur.commit()

        print(" Table created successfully")
    except Exception as error:
        print(f"Error:  {error}")
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    create_table()

    
