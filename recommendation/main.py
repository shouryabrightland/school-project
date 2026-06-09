import sqlite3
import sys
import random

DATABASE_NAME = "movies.db"
current_user_id = None


# ---------------- DB ----------------

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def check_database():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM users")
        cursor.execute("SELECT 1 FROM movies")
        cursor.execute("SELECT 1 FROM ratings")
        connection.close()
        return True
    except:
        return False


if not check_database():
    print("Database is broken. Run initialize.py")
    sys.exit()


# ---------------- UI ----------------

def line():
    print("-" * 60)


def header(text):
    width = 60
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width)

# ---------------- MENU ENGINE ----------------

def run_menu(title, menu_options):

    while True:
        header(title)

        keys = list(menu_options.keys())
        i = 1

        for key in keys:
            print(str(i) + ". " + key)
            i += 1

        line()

        choice = input("Select option: ")

        if not choice.isdigit():
            print("Invalid choice")
            continue

        choice = int(choice)

        if choice < 1 or choice > len(keys):
            print("Invalid choice")
            continue

        selected_key = keys[choice - 1]
        result = menu_options[selected_key]()

        if result == "EXIT":
            return


# ---------------- AUTH ----------------

def register_user():
    line()
    username = input("Username: ")
    password = input("Password: ")
    line()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )
        connection.commit()
        print("Registration successful")
    except:
        print("Username already exists")

    connection.close()


def login_user():
    global current_user_id

    line()
    username = input("Username: ")
    password = input("Password: ")
    line()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    connection.close()

    if user:
        current_user_id = user[0]
        return "LOGIN_SUCCESS"
    else:
        print("Invalid credentials")
        return None


# ---------------- DATA ----------------

def fetch_home_data():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT m.id, m.name, COALESCE(AVG(r.rating),0)
        FROM movies m
        LEFT JOIN ratings r ON m.id=r.movie_id
        GROUP BY m.id
        ORDER BY AVG(r.rating) DESC
        LIMIT 3
    """)
    trending = cursor.fetchall()

    cursor.execute("""
        SELECT m.id, m.name, COALESCE(AVG(r.rating),0)
        FROM movies m
        LEFT JOIN ratings r ON m.id=r.movie_id
        WHERE m.genre=(
            SELECT m2.genre
            FROM ratings r2
            JOIN movies m2 ON r2.movie_id=m2.id
            WHERE r2.user_id=?
            GROUP BY m2.genre
            ORDER BY AVG(r2.rating) DESC
            LIMIT 1
        )
        AND m.id NOT IN (SELECT movie_id FROM ratings WHERE user_id=?)
        GROUP BY m.id
        ORDER BY AVG(r.rating) DESC
        LIMIT 3
    """, (current_user_id, current_user_id))

    recommended = cursor.fetchall()

    cursor.execute("SELECT id,name FROM movies")
    all_movies = cursor.fetchall()

    connection.close()

    return trending, recommended, all_movies


# ---------------- EXPLORE ----------------

def show_explore(all_movies, trending, recommended):

    excluded = []

    for m in trending:
        excluded.append(m[0])

    for m in recommended:
        excluded.append(m[0])

    pool = []

    for m in all_movies:
        if m[0] not in excluded:
            pool.append(m)

    if len(pool) == 0:
        return

    random.shuffle(pool)
    pool = pool[:5]

    print("\nEXPLORE MOVIES")

    i = 1
    for m in pool:
        print(str(i) + ". [" + str(m[0]) + "] " + m[1])
        i += 1


# ---------------- MOVIE PAGE ----------------

def open_movie(movie_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT m.id, m.name, m.genre, m.description, COALESCE(AVG(r.rating),0)
        FROM movies m
        LEFT JOIN ratings r ON m.id=r.movie_id
        WHERE m.id=?
        GROUP BY m.id
    """, (movie_id,))

    movie = cursor.fetchone()

    if not movie:
        print("Movie not found")
        return

    while True:
        header(movie[1])

        print("Genre:", movie[2])
        print("Rating:", round(movie[4], 1))
        line()
        print(movie[3])
        line()

        cursor.execute(
            "SELECT rating FROM ratings WHERE user_id=? AND movie_id=?",
            (current_user_id, movie_id)
        )

        user_rating = cursor.fetchone()
        print("Your Rating:", user_rating[0] if user_rating else "Not Rated")

        line()
        print("1. Rate Movie")
        print("2. Back")
        line()

        choice = input("> ")

        if choice == "1":
            rating = input("Enter rating (1-5): ")

            if not rating.isdigit():
                continue

            rating = int(rating)

            if rating < 1 or rating > 5:
                print("Invalid rating")
                continue

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT OR REPLACE INTO ratings(user_id,movie_id,rating)
                VALUES(?,?,?)
            """, (current_user_id, movie_id, rating))

            conn.commit()
            conn.close()

        elif choice == "2":
            return


def select_movie():
    movie_id = input("Enter Movie ID: ")
    if movie_id.isdigit():
        open_movie(int(movie_id))


def my_ratings():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT m.name, r.rating
        FROM ratings r
        JOIN movies m ON m.id=r.movie_id
        WHERE r.user_id=?
    """, (current_user_id,))

    ratings = cursor.fetchall()
    connection.close()

    header("MY RATINGS")

    if not ratings:
        print("No ratings yet")
        input()
        return

    total = 0

    for r in ratings:
        print(r[0], "★", r[1])
        total += r[1]

    line()
    print("Average:", round(total / len(ratings), 2))
    input()


# ---------------- HOME ----------------

def home_screen():

    def home_logic():
        trending, recommended, all_movies = fetch_home_data()

        header("HOME")

        print("\nTRENDING")
        letter = "ABC"
        i = 0
        for m in trending:
            print(letter[i] + ". [" + str(m[0]) + "] " + m[1])
            i += 1

        line()

        print("\nRECOMMENDED")
        i = 1
        for m in recommended:
            print(str(i) + ". [" + str(m[0]) + "] " + m[1])
            i += 1

        line()

        show_explore(all_movies, trending, recommended)
        line()

    def select_movie_action():
        select_movie()

    def my_ratings_action():
        my_ratings()

    def refresh():
        return None

    def logout():
        return "EXIT"

    while True:

        home_logic()

        run_menu("HOME MENU", {
            "Select Movie": select_movie_action,
            "My Ratings": my_ratings_action,
            "Refresh": refresh,
            "Logout": logout
        })

        break


# ---------------- MAIN MENU ----------------

def start_login():
    result = login_user()
    if result == "LOGIN_SUCCESS":
        home_screen()


def start_register():
    register_user()

def exit_app():
    sys.exit()

run_menu("MOVIE RECOMMENDATION SYSTEM", {
    "Login": start_login,
    "Register": start_register,
    "Exit": exit_app
})