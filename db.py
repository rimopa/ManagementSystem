import sqlite3
path = "monjas.db"
connection = sqlite3.connect(path)
cur = connection.cursor()

ROOMS = 40

"""
Bookings:
state: 0 - Pending
       1 - Confirmed
           2 - Finished
           3 - Canceled by User
           4 - Canceled by Admin
           5 - In Progress
food: 0    - No food
          1    - Yes food
food_pref: preferences (may be null)
startdate, finishdate: YYYY-MM-DD (ISO8601)
contact: phone or email
comment: any additional info
price: total price in usd

Rooms:
type: 0 - private bathroom
      1 - shared bathroom

Staff:
name: full name
dni: identification number
basic_salary: basic monthly salary in usd
startdate: date of hire YYYY-MM-DD (ISO8601)
overtime: overtime pay in usd per hour
weekly_hours: number of hours worked per week

Users:
username: unique username
password: raw password
admin: 0 - regular user
           1 - admin user

Room-Booking:
double: 0 - single room
        1 - double room

People:
nane: full name
dni: identification number
age: age in years

Booking-People:
Means that a person is associated with a booking.
"""


class Booking:
    def __init__(self, id, user_id, state, food, food_pref, startDate, finishDate, comment, contact, price):
        self.id = id
        self.user_id = user_id
        self.state = state
        self.startDate = startDate
        self.finishDate = finishDate
        self.food = food
        self.comment = comment
        self.contact = contact
        self.price = price
        self.food_pref = food_pref


def initdb():
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS "Bookings" (
                "booking_id"	INTEGER NOT NULL UNIQUE,
                "user_id"	INTEGER NOT NULL,
                "state"	INTEGER NOT NULL CHECK (state IN (0, 1, 2, 3, 4)),
                "startdate"	TEXT NOT NULL,
                "finishdate"	TEXT NOT NULL,
                "food"	INTEGER NOT NULL CHECK (food IN (0, 1)),
                "food_pref"	TEXT,
                "comment"	TEXT,
                "contact"	TEXT NOT NULL,
                "price"	INTEGER NOT NULL,
                PRIMARY KEY("booking_id" AUTOINCREMENT),
                FOREIGN KEY("user_id") REFERENCES "Users"("user_id")
        );

        CREATE TABLE IF NOT EXISTS "Rooms" (
                "room_id"	INTEGER NOT NULL UNIQUE,
                "type"	INTEGER NOT NULL CHECK (type IN (0, 1)),
                PRIMARY KEY("room_id" AUTOINCREMENT)
        );

        CREATE TABLE IF NOT EXISTS "Staff" (
                "employee_id"	INTEGER NOT NULL UNIQUE,
                "name"	TEXT NOT NULL,
                "dni"	INTEGER NOT NULL,
                "basic_salary"	INTEGER,
                "startdate"	INTEGER NOT NULL,
                "overtime"	INTEGER,
                "weekly_hours"	INTEGER NOT NULL,
                PRIMARY KEY("employee_id" AUTOINCREMENT)
        );

        CREATE TABLE IF NOT EXISTS "Users" (
                "user_id"	INTEGER NOT NULL UNIQUE,
                "username"	TEXT NOT NULL UNIQUE,
                "password"	TEXT NOT NULL,
                "admin"	INTEGER NOT NULL CHECK (admin IN (0, 1)),
                PRIMARY KEY("user_id" AUTOINCREMENT)
        );

        CREATE TABLE IF NOT EXISTS "Room-Booking" (
                "booking_id"	INTEGER NOT NULL,
                "room_id"	INTEGER NOT NULL,
                "double"	INTEGER NOT NULL CHECK (double IN (0, 1)),
                PRIMARY KEY("booking_id","room_id"),
                FOREIGN KEY("booking_id") REFERENCES "Bookings"("booking_id"),
                FOREIGN KEY("room_id") REFERENCES "Rooms"("room_id")
        );
        
    CREATE TABLE IF NOT EXISTS "People" (
                "person_id"	INTEGER NOT NULL,
                "name"	TEXT NOT NULL,
                "dni"	INTEGER NOT NULL,
                "age"	INTEGER NOT NULL,
                PRIMARY KEY("person_id")
        );
        
    CREATE TABLE IF NOT EXISTS "Booking-People" (
                "person_id"	INTEGER NOT NULL,
                "booking_id"	INTEGER NOT NULL,
                PRIMARY KEY("person_id", "booking_id"),
                FOREIGN KEY("person_id") REFERENCES "Room-People"("person_id"),
                FOREIGN KEY("booking_id") REFERENCES "Bookings"("booking_id")
        );
        """)
    connection.commit()


def reserAll():
    cur.executescript("""
        DELETE FROM "Room-Booking";
        DELETE FROM "Rooms";
        DELETE FROM "Staff";
        DELETE FROM "Users";
        DELETE FROM "Bookings";
        DELETE FROM "People";
        DELETE FROM "Booking-People";""")
    resetRooms()
    connection.commit()


def resetRooms():
    cur.execute("DELETE FROM Rooms")
    for i in range(40):
        room_type = 1 if i < 30 else 0  # First 30 rooms type 1, last 10 type 0
        cur.execute("INSERT INTO Rooms (type) VALUES (?)", (room_type,))
    connection.commit()


def addUser(username, password):
    try:
        cur.execute("""
                        INSERT INTO Users(username, password, admin)
                        VALUES(?, ?, 0)""", (username, password))
        connection.commit()
        user_id = cur.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None


def addBooking(b: Booking):
    cur.execute("""
        INSERT INTO Bookings(user_id, state, startdate, finishdate, food, food_pref, comment, contact, price)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (b.user_id, b.state, b.startdate, b.finishdate, b.food, b.food_pref, b.comment, b.contact, b.price))
    connection.commit()
    booking_id = cur.lastrowid
    return booking_id


def modifyBooking(b: Booking):
    fields = []
    values = []
    if b.state is not None:
        fields.append("state = ?")
        values.append(b.state)
    if b.startdate is not None:
        fields.append("startdate = ?")
        values.append(b.startdate)
    if b.finishdate is not None:
        fields.append("finishdate = ?")
        values.append(b.finishdate)
    if b.food is not None:
        fields.append("food = ?")
        values.append(b.food)
    if b.food_pref is not None:
        fields.append("food_pref = ?")
        values.append(b.food_pref)
    if b.comment is not None:
        fields.append("comment = ?")
        values.append(b.comment)
    if b.contact is not None:
        fields.append("contact = ?")
        values.append(b.contact)
    if b.price is not None:
        fields.append("price = ?")
        values.append(b.price)
    values.append(b.id)
    sql = f"UPDATE Bookings SET {', '.join(fields)} WHERE booking_id = ?"
    cur.execute(sql, values)
    connection.commit()


def getBooking(id):
    cur.execute("""
                SELECT * FROM Bookings WHERE booking_id=?
        """, (id,))
    booking = cur.fetchone()
    print(booking)
    if booking:
        return booking
    else:
        return None


def getUserid(username):
    cur.execute("""
                SELECT user_id FROM Users WHERE username=?
        """, (username,))
    user = cur.fetchone()
    if user:
        return user[0]
    else:
        return None


def getUsersBookings(user_id):
    cur.execute("""
                SELECT * FROM Bookings WHERE user_id=?
        """, (user_id,))
    bookings = cur.fetchall()
    return bookings


def getAllBookings():
    cur.execute("""
                SELECT * FROM Bookings
        """)
    bookings = []
    for booking in cur.fetchall():
        bookings.append(Booking(booking))
    return bookings


def getBookingsFromDate(startdate, finishdate):
    cur.execute("""
                SELECT * FROM Bookings WHERE NOT(date(finishdate) <= date(?) OR date(startdate) >= date(?))
        """, (startdate, finishdate))
    bookings = cur.fetchall()
    return bookings


def getAvailableRooms(startDate, finishDate, roomType=None, shared_bathroom=None):
    """Return available rooms between startDate and finishDate.

    Arguments:
    - startDate, finishDate: ISO date strings (YYYY-MM-DD)
    - roomType: if not None, filter by Rooms.type (0 = private bathroom, 1 = shared)
    - shared_bathroom: if not None, boolean indicating whether the caller
      requires a shared bathroom (True) or not (False). This is equivalent to
      roomType=1 when True, roomType=0 when False. If both are provided,
      `roomType` takes precedence.

    Side-effect: sets module-level `availableRooms` list (kept for compatibility
    with existing code that references `db.availableRooms`). Returns the list
    of rows fetched from the database.
    """
    sql = """
        SELECT * FROM Rooms WHERE room_id NOT IN(
            SELECT rb.room_id FROM "Room-Booking" rb
            JOIN Bookings b ON rb.booking_id=b.booking_id
            WHERE NOT(date(b.finishdate) <= date(?) OR date(b.startdate) >= date(?))
        )"""
    params = [startDate, finishDate]

    # Determine final type filter
    final_type = None
    if roomType is not None:
        final_type = roomType
    elif shared_bathroom is not None:
        final_type = 1 if shared_bathroom else 0

    if final_type is not None:
        sql = sql.rstrip() + " AND type = ?"
        params.append(final_type)

    cur.execute(sql, tuple(params))
    rooms = cur.fetchall()
    return rooms


def getUser(user_id):
    cur.execute("""
                SELECT * FROM Users WHERE user_id=?
        """, (user_id,))
    user = cur.fetchone()
    if user:
        return user
    else:
        return None


def addpeople(People: list):
    person_ids = []
    for person in People:
        cur.execute("""
            INSERT INTO People(name, age,dni)
            VALUES(?, ?)
        """, (person['name'], person['dni']))
        connection.commit()
        person_id = cur.lastrowid
        person_ids.append(person_id)
    return person_ids


def userPasswordMatches(user_id, password):
    cur.execute("""
                SELECT password FROM Users WHERE user_id=?
        """, (user_id,))
    user = cur.fetchone()
    if user:
        if user[0] == password:
            return True
        else:
            return False
    else:
        return None


def isAdmin(user_id):
    cur.execute("""
                SELECT admin FROM Users WHERE user_id=?
        """, (user_id,))
    user = cur.fetchone()
    if user and user[0] == 1:
        return True
    else:
        return False


initdb()
# addBooking(getUserid("admin"), 0, "2024-07-01",
#    "2024-07-10", 2, 1, None, "+54 351 665-2991", 0)
addUser("admin", "adminwashere")
get = getUsersBookings(getUserid("admin"))
if get:
    print(get[1][0])
print(getUser(getUserid("admin")))
