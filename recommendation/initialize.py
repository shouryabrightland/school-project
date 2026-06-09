import sqlite3
import json
import os

DB = "movies.db"


def create_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE movies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        genre TEXT,
        description TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE ratings(
        user_id INTEGER,
        movie_id INTEGER,
        rating INTEGER,
        PRIMARY KEY(user_id, movie_id)
    )
    """)

    con.commit()
    con.close()


def refresh_movies():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    with open("movies.json", "r", encoding="utf-8") as f:
        movies = json.load(f)

    for m in movies:
        cur.execute("""
        INSERT OR REPLACE INTO movies(name, genre, description)
        VALUES(?,?,?)
        """, (m["name"], m["genre"], m["description"]))

    con.commit()
    con.close()


# If db missing -> rebuild
if not os.path.exists(DB):
    create_db()
    print("Database created.")
else:
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT 1 FROM users")
        cur.execute("SELECT 1 FROM movies")
        cur.execute("SELECT 1 FROM ratings")
        con.close()
    except:
        os.remove(DB)
        create_db()
        print("Broken DB fixed.")

refresh_movies()
print("Movies loaded.")