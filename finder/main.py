# Railway Route Finder
# Class 12 CBSE Project

import sqlite3

# ---------------- DATABASE ----------------

con=sqlite3.connect("railway.db")
cur=con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stations(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS routes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
source TEXT,
destination TEXT,
distance INTEGER,
time INTEGER,
fare INTEGER
)
""")

con.commit()

def execute(q,v=()):
    cur.execute(q,v)
    con.commit()

def fetchone(q,v=()):
    cur.execute(q,v)
    return cur.fetchone()

def fetchall(q,v=()):
    cur.execute(q,v)
    return cur.fetchall()

# ---------------- COMMON ----------------

def pause():
    input("\nPress Enter To Continue...")

def back():
    return "BACK"

def close_program():
    con.close()
    quit()

def run_menu(title,menu):

    while True:

        print("\n"+"="*40)
        print(title.center(40))
        print("="*40)

        for key,value in menu.items():
            print(f"{key}. {value[0]}")

        try:
            choice=int(input("\nEnter Choice : "))
        except:
            print("Invalid Choice")
            continue

        if choice not in menu:
            print("Invalid Choice")
            continue

        result=menu[choice][1]()

        if result=="BACK":
            return

# ---------------- STATION FUNCTIONS ----------------

def add_station():
    name=input("Station Name : ").title()
    try:
        execute("INSERT INTO stations(name) VALUES(?)",(name,))
        print("Station Added")

    except:
        print("Station Already Exists")

    pause()

def update_station():

    old=input("Current Name : ").title()
    new=input("New Name : ").title()

    execute("UPDATE stations SET name=? WHERE name=?",(new,old))
    execute("UPDATE routes SET source=? WHERE source=?",(new,old))
    execute("UPDATE routes SET destination=? WHERE destination=?",(new,old))

    print("Station Updated")
    pause()

def delete_station():

    name=input("Station Name : ").title()

    execute("DELETE FROM routes WHERE source=? OR destination=?",(name,name))
    execute("DELETE FROM stations WHERE name=?",(name,))

    print("Station Deleted")
    pause()

def view_stations():

    data=fetchall("SELECT * FROM stations")

    print("\nAvailable Stations\n")

    for row in data:
        print(row[0],"-",row[1])

    pause()

# ---------------- ROUTE FUNCTIONS ----------------

def add_route():

    source=input("Source : ").title()
    destination=input("Destination : ").title()

    if not fetchone("SELECT * FROM stations WHERE name=?",(source,)):
        print("Source Station Not Found")
        pause()
        return

    if not fetchone("SELECT * FROM stations WHERE name=?",(destination,)):
        print("Destination Station Not Found")
        pause()
        return

    distance=int(input("Distance (km) : "))
    time=int(input("Travel Time (hrs) : "))
    fare=int(input("Fare : "))

    execute(
        "INSERT INTO routes(source,destination,distance,time,fare) VALUES(?,?,?,?,?)",
        (source,destination,distance,time,fare)
    )

    print("Route Added")
    pause()

def update_route():

    source=input("Source : ").title()
    destination=input("Destination : ").title()

    if not fetchone(
        "SELECT * FROM routes WHERE source=? AND destination=?",
        (source,destination)
    ):
        print("Route Not Found")
        pause()
        return

    distance=int(input("New Distance : "))
    time=int(input("New Time : "))
    fare=int(input("New Fare : "))

    execute(
        "UPDATE routes SET distance=?,time=?,fare=? WHERE source=? AND destination=?",
        (distance,time,fare,source,destination)
    )

    print("Route Updated")
    pause()

def delete_route():

    source=input("Source : ").title()
    destination=input("Destination : ").title()

    execute(
        "DELETE FROM routes WHERE source=? AND destination=?",
        (source,destination)
    )

    print("Route Deleted")
    pause()

def view_routes():

    data=fetchall(
        "SELECT source,destination,distance,time,fare FROM routes"
    )

    print()

    for row in data:
        print(
            f"{row[0]} -> {row[1]} | "
            f"{row[2]} km | "
            f"{row[3]} hrs | "
            f"₹{row[4]}"
        )

    pause()

# ---------------- GRAPH ----------------

def build_graph():

    graph={}

    data=fetchall(
        "SELECT source,destination,distance,time,fare FROM routes"
    )

    for row in data:

        graph.setdefault(row[0],[]).append({
            "destination":row[1],
            "distance":row[2],
            "time":row[3],
            "fare":row[4]
        })

    return graph

best_cost=None
best_route={}

def search(city,destination,route,mode,graph):

    global best_cost,best_route

    if city==destination:

        if best_cost is None or route[mode]<best_cost:
            best_cost=route[mode]
            best_route=route.copy()

        return

    for edge in graph.get(city,[]):

        next_city=edge["destination"]

        if next_city in route["path"]:
            continue

        new_route={
            "path":route["path"]+[next_city],
            "distance":route["distance"]+edge["distance"],
            "time":route["time"]+edge["time"],
            "fare":route["fare"]+edge["fare"],
            "stops":route["stops"]+1
        }

        search(next_city,destination,new_route,mode,graph)

def find_route(mode):

    global best_cost,best_route

    source=input("Source : ").title()
    destination=input("Destination : ").title()

    graph=build_graph()

    best_cost=None
    best_route={}

    route={
        "path":[source],
        "distance":0,
        "time":0,
        "fare":0,
        "stops":0
    }

    search(source,destination,route,mode,graph)

    if best_cost is None:
        print("Route Not Found")
        pause()
        return

    print("\nBEST ROUTE")
    print("-"*40)

    print("Path :"," -> ".join(best_route["path"]))
    print("Distance :",best_route["distance"],"km")
    print("Travel Time :",best_route["time"],"hrs")
    print("Stops :",best_route["stops"])
    print("Fare : ₹",best_route["fare"])

    pause()

# ---------------- FINDER ----------------

def shortest_route():
    find_route("distance")

def fastest_route():
    find_route("time")

def cheapest_route():
    find_route("fare")

def minimum_stops():
    find_route("stops")

# ---------------- MENUS ----------------

station_menu={
1:("Add Station",add_station),
2:("Update Station",update_station),
3:("Delete Station",delete_station),
4:("View Stations",view_stations),
5:("Back",back)
}

route_menu={
1:("Add Route",add_route),
2:("Update Route",update_route),
3:("Delete Route",delete_route),
4:("View Routes",view_routes),
5:("Back",back)
}

finder_menu={
1:("Shortest Route",shortest_route),
2:("Fastest Route",fastest_route),
3:("Cheapest Route",cheapest_route),
4:("Minimum Stops Route",minimum_stops),
5:("Back",back)
}

main_menu={
1:("Station Management",lambda:run_menu("STATION MANAGEMENT",station_menu)),
2:("Route Management",lambda:run_menu("ROUTE MANAGEMENT",route_menu)),
3:("Route Finder",lambda:run_menu("ROUTE FINDER",finder_menu)),
4:("Exit",close_program)
}

# ---------------- START ----------------

run_menu("RAILWAY ROUTE FINDER",main_menu)

