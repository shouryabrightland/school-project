# Database Module
import sqlite3

con = sqlite3.connect("railway.db")
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS stations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE)
""")

cur.execute("""CREATE TABLE IF NOT EXISTS routes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    destination TEXT,
    distance INTEGER,
    time INTEGER,
    sleeper INTEGER,
    ac3 INTEGER,
    ac2 INTEGER)""")

con.commit()

def execute(query, values=()):
    cur.execute(query, values)
    con.commit()

def fetchone(query, values=()):
    cur.execute(query, values)
    return cur.fetchone()

def fetchall(query, values=()):
    cur.execute(query, values)
    return cur.fetchall()

def close():
    con.close()