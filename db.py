import sqlite3

PATH = "monjas.db"
connection = sqlite3.connect(PATH)
cur = connection.cursor()

ROOMS = 40

"""
Bookings:
state: 0 - Pending
       1 - Confirmed
       2 - Finished
       3 - Canceled (by User)
       4 - Declined (by Admin)
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
admin:  0 - regular user
        1 - admin user

Room-Booking:
double: 0 - single room
        1 - double room

People:
name: full name
dni: identification number
age: age in years

Booking-People:
Means that a person is associated with a booking.
"""


class Booking:
    def __init__(self, id: int, user_id: int, state: int, food: bool, food_pref: str,
                 startDate: str, finishDate: str, comment: str, contact: str, price: int):
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

    def returnTuple(self):
        return (self.id, self.user_id, self.state, self.startDate, self.finishDate,
                self.food, self.food_pref, self.comment, self.contact, self.price)


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
                "dni"	INTEGER NOT NULL UNIQUE,
                "age"	INTEGER NOT NULL,
                PRIMARY KEY("person_id")
        );
        
    CREATE TABLE IF NOT EXISTS "Booking-Person" (
                "person_id"	INTEGER NOT NULL,
                "booking_id"	INTEGER NOT NULL,
                PRIMARY KEY("person_id", "booking_id"),
                FOREIGN KEY("person_id") REFERENCES "People"("person_id"),
                FOREIGN KEY("booking_id") REFERENCES "Bookings"("booking_id")
        );
        """)
    connection.commit()


def resetAll():
    cur.executescript("""
        DELETE FROM "Room-Booking";
        DELETE FROM "Rooms";
        DELETE FROM "Staff";
        DELETE FROM "Users";
        DELETE FROM "Bookings";
        DELETE FROM "People";
        DELETE FROM "Booking-Person";
        """)
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
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (b.returnTuple()[1:]))
    connection.commit()
    booking_id = cur.lastrowid
    return booking_id


def tryNewBooking(booking: Booking, people: list, roomType) -> int:
    available_rooms = getAvailableRooms(
        booking.startDate, booking.finishDate, roomType)
    if len(available_rooms) <= round((len(people))/2):
        return None
    room_ids = available_rooms[:round((len(people)+1)/2)]
    double_flags = []
    person_ids = addPeople(people)
    addPeopletoBooking(booking_id, person_ids)
    addRoomstoBooking(booking_id, room_ids, double_flags)
    booking_id = addBooking(booking, roomType)
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


def getUserId(username):
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


def getAvailableRooms(startDate, finishDate, roomType=None):
    """Return available rooms between startDate and finishDate with optional type."""
    sql = """
    SELECT r.*
    FROM Rooms r
    LEFT JOIN "Room-Booking" rb
        ON r.room_id = rb.room_id
    LEFT JOIN Bookings b
        ON rb.booking_id = b.booking_id
        AND NOT (b.finishdate <= ? OR b.startdate >= ?)
    WHERE b.booking_id IS NULL
    """
    params = [startDate, finishDate]

    if roomType is not None:
        sql += " AND r.type = ?"
        params.append(roomType)
    cur.execute(sql, tuple(params))
    rooms = cur.fetchall()
    return [room[0] for room in rooms]


def getUser(user_id):
    cur.execute("""
                SELECT * FROM Users WHERE user_id=?
        """, (user_id,))
    user = cur.fetchone()
    if user:
        return user
    else:
        return None


def addPeople(People: list):
    if not People:
        return []

    # Extract all DNIs from the input list
    dnis = [person['dni'] for person in People]
    dni_to_person = {person['dni']: person for person in People}

    # Get existing people
    cur.execute(f"""
        SELECT person_id, dni FROM People WHERE dni IN ({','.join('?' * len(dnis))})
    """, dnis)
    # Map existing DNIs to their IDs
    existing_ids = {}
    for person_id, dni in cur.fetchall():
        existing_ids[dni] = person_id
    person_ids = []
    # Insert people who don't exist yet
    for dni in dnis:
        if dni in existing_ids:
            # Use existing id
            person_ids.append(existing_ids[dni])
        else:
            # Insert new person
            person = dni_to_person[dni]
            cur.execute("""
                INSERT INTO People(name, age, dni)
                VALUES(?, ?, ?)
            """, (person['name'], person['age'], person['dni']))
            connection.commit()
            person_ids.append(cur.lastrowid)
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


def cancelBooking(booking_id):
    cur.execute("""
        UPDATE Bookings
        SET state = 3
        WHERE booking_id = ?
    """, (booking_id,))
    connection.commit()


def declineBooking(booking_id):
    cur.execute("""
        UPDATE Bookings
        SET state = 4
        WHERE booking_id = ?
    """, (booking_id,))
    connection.commit()


def acceptBooking(booking_id):
    cur.execute("""
        UPDATE Bookings
        SET state = 1
        WHERE booking_id = ?
    """, (booking_id,))
    connection.commit()


def addPeopletoBooking(booking_id, person_ids):
    for person_id in person_ids:
        cur.execute("""
            INSERT INTO "Booking-Person"(person_id, booking_id)
            VALUES(?, ?)
        """, (person_id, booking_id))
    connection.commit()


def addRoomstoBooking(booking_id, room_ids, double_flags):
    for room_id, double in zip(room_ids, double_flags):
        cur.execute("""
            INSERT INTO "Room-Booking"(booking_id, room_id, double)
            VALUES(?, ?, ?)
        """, (booking_id, room_id, double))
    connection.commit()
