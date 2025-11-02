try:
    import copy
    import csv
    import os
    import re
    import db
    import sqlite3
    import tkcalendar
    from datetime import date
    from tkinter import *
    from tkinter import ttk
except ModuleNotFoundError as error:
    print("One or more modules not found.\nAborting...")
    raise error

# <consts>
MAX_YEAR = date.today().year + 5
MAX_ROOMS = 48
MAX_PEOPLE = 2
FOOD_PRICE_PER_NIGHT = 5000
ROOM_PRICE_PER_NIGHT = (60000, 85000, 50000, 55000)
# </consts>


# <utility functions>
def without(s: str, charlst: tuple):
    """Return str without characters that are on charlst"""
    return "".join([c for c in s if c not in charlst])


def tryNewBooking(Booking: db.Booking, people: list, roomType) -> int:
    """Tries to add a new booking to the database. Returns True if successful, False otherwise."""
    available_rooms = db.getAvailableRooms(
        Booking.startDate, Booking.finishDate, roomType)

    print(Booking.startDate, Booking.finishDate, roomType)
    print(type(Booking.startDate), type(Booking.finishDate), type(roomType))
    print(available_rooms)

    if len(available_rooms) > round((len(people))/2):
        booking_id = db.addBooking(Booking)
        return booking_id
    else:
        return None


def formatBookings(bkngs):
    a = copy.deepcopy(bkngs)
    for b in a:
        # state:
        if b["state"] == 0:
            b["state"] = "Por aceptar"
        elif b["state"] == 1:
            b["state"] = "Aceptada/En espera"
        elif b["state"] == 2:
            b["state"] = "Terminada"
        elif b["state"] == 3:
            b["state"] = "Rechazada"
        elif b["state"] == 4:
            b["state"] = "Activa (realizándose)"
        # names:
        b["names"] = ", ".join(b["names"])
        # ages:
        b["ages"] = ", ".join(b["ages"])
        # food:
        if b["food"] == "1":
            b["food"] = "Incluida"
        elif b["food"] == "0":
            b["food"] = "No incluida"
        elif b["food"]:
            b["food"] = "Incluida. " + b["food"]
        # roomType:
        if b["roomType"] == 0:
            b["roomType"] = "Privado"
        elif b["roomType"] == 1:
            b["roomType"] = "Compartido"
        # startDate:
        b["startDate"] = date.fromisoformat(b["startDate"])
        # finishDate:
        b["finishDate"] = date.fromisoformat(b["finishDate"])
    return a
# </utility functions>


# <modal windows>
def confirmationWindow(parent, msg):
    result = {'value': None}

    def yBtt():
        result['value'] = True
        confw.destroy()

    def nBtt():
        result['value'] = False
        confw.destroy()

    confw = Toplevel(parent)
    confw.title("Confirmación")
    confw.resizable(False, False)
    confw.grab_set()

    mainframe = ttk.Frame(confw, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=N)

    ttk.Label(mainframe, text=msg, wraplength=300).grid(
        row=0, sticky=(W, S, E))
    ttk.Button(mainframe, text="Sí", command=yBtt).grid(
        column=0, row=1, sticky=(W, S), pady=10)
    ttk.Button(mainframe, text="No", command=nBtt).grid(
        column=1, row=1, sticky=(E, S), pady=10)

    confw.wait_window()
    return result['value']


def InformativeWindow(parent, msg):
    infw = Toplevel(parent)
    infw.title("Información")
    infw.resizable(False, False)
    Label(infw, text=msg, wraplength=300, padx=20, pady=20).pack()
    infw.grab_set()
    infw.focus_set()
# </modal windows>


# <Frame Manager>
class FrameManager:
    def __init__(self, root):
        self.root = root
        self.frames = {}
        self.current_frame = None

    def add_frame(self, name, frame):
        self.frames[name] = frame
        frame.grid(row=0, column=0, sticky=(N, S, E, W))
        frame.grid_remove()

    def show_frame(self, name, **kwargs):
        if self.current_frame:
            self.current_frame.grid_remove()
        self.current_frame = self.frames[name]
        if hasattr(self.current_frame, 'refresh'):
            self.current_frame.refresh(**kwargs)
        self.current_frame.grid()
# </Frame Manager>


# <Main Menu Frame>
class MainMenuFrame(ttk.Frame):
    def __init__(self, parent, frame_manager, app):
        super().__init__(parent)
        self.frame_manager = frame_manager
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        mainframe = ttk.Frame(self, padding="20 20 20 20")
        mainframe.grid(column=0, row=0, sticky=(N, S, E, W))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.welcomeMsg = StringVar()
        self.welcomeMsg.set("Bienvenido")

        ttk.Label(mainframe, textvariable=self.welcomeMsg,
                  font=('Arial', 16, 'bold')).grid(row=0, sticky=(W, S, E), pady=20)

        self.login_button = ttk.Button(mainframe, text="Iniciar sesión",
                                       command=self.go_to_login)
        self.login_button.grid(row=1, sticky=(W, S, E), pady=10)

        self.sign_out_button = ttk.Button(mainframe, text="Cerrar sesión",
                                          command=self.log_out)
        self.sign_out_button.grid(row=1, sticky=(W, E), pady=10)
        self.sign_out_button.grid_remove()

        self.manage_bookings_button = ttk.Button(mainframe, text="Administrar reservas",
                                                 command=self.go_to_bookings)
        self.manage_bookings_button.grid(row=3, sticky=(W, E), pady=10)
        self.manage_bookings_button.grid_remove()

        self.new_booking_button = ttk.Button(mainframe, text="Crear una nueva reserva",
                                             command=self.go_to_new_booking)
        self.new_booking_button.grid(row=4, sticky=(W, E), pady=10)
        self.new_booking_button.grid_remove()

        mainframe.columnconfigure(0, weight=1)

    def go_to_login(self):
        self.frame_manager.show_frame("login")

    def go_to_bookings(self):
        self.frame_manager.show_frame("bookings")

    def go_to_new_booking(self):
        self.frame_manager.show_frame("new_booking")

    def log_out(self):
        self.app.cUser = 0
        self.app.cAdmin = 0
        self.refresh()

    def refresh(self):
        if self.app.cUser:
            # Get username from user ID
            user = db.getUser(self.app.cUser)
            self.welcomeMsg.set(f"Bienvenido, {user[1]}")
            self.login_button.grid_remove()
            self.sign_out_button.grid()
            self.manage_bookings_button.grid()
            if self.app.cAdmin:
                self.new_booking_button.grid_remove()
            else:
                self.new_booking_button.grid()
        else:
            self.welcomeMsg.set("Bienvenido")
            self.sign_out_button.grid_remove()
            self.manage_bookings_button.grid_remove()
            self.new_booking_button.grid_remove()
            self.login_button.grid()
# </Main Menu Frame>


# <Login Frame>
class LoginFrame(ttk.Frame):
    def __init__(self, parent, frame_manager, app):
        super().__init__(parent)
        self.frame_manager = frame_manager
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        mainframe = ttk.Frame(self, padding="20 20 20 20")
        mainframe.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ttk.Label(mainframe, text="Iniciar Sesión",
                  font=('Arial', 16, 'bold')).grid(row=0, columnspan=2, pady=20)

        ttk.Label(mainframe, text="Usuario").grid(
            row=1, column=0, sticky=W, pady=5)
        self.usStr = StringVar()
        ttk.Entry(mainframe, textvariable=self.usStr).grid(
            row=1, column=1, pady=5)

        ttk.Label(mainframe, text="Contraseña").grid(
            row=2, column=0, sticky=W, pady=5)
        self.pwStr = StringVar()
        ttk.Entry(mainframe, textvariable=self.pwStr,
                  show="*").grid(row=2, column=1, pady=5)

        ttk.Button(mainframe, text='Iniciar sesión',
                   command=self.check_login).grid(row=3, columnspan=2, pady=10)

        ttk.Button(mainframe, text="¿Primera vez? Cree un nuevo usuario",
                   command=self.go_to_signup).grid(row=4, columnspan=2)

        ttk.Button(mainframe, text="← Volver",
                   command=self.go_back).grid(row=5, columnspan=2, pady=10)

        self.bind("<Return>", lambda e: self.check_login())

    def check_login(self):
        givenUser = self.usStr.get()
        givenPassword = self.pwStr.get()

        if "," in givenPassword + givenUser:
            InformativeWindow(
                self, 'No incluya comas (",") en el usuario ni contraseña')
            return
        userId = db.getUserId(givenUser)
        if userId is None:
            if confirmationWindow(self, "Usuario no encontrado. ¿Quiere crear un nuevo usuario?"):
                self.go_to_signup()
            return
        if not db.userPasswordMatches(userId, givenPassword):
            InformativeWindow(
                self, "Contraseña incorrecta. Intente nuevamente")
            return
        self.app.cUser = userId
        self.app.cAdmin = db.isAdmin(userId)
        self.usStr.set("")
        self.pwStr.set("")
        self.frame_manager.show_frame("main")

    def go_to_signup(self):
        self.frame_manager.show_frame("signup")

    def go_back(self):
        self.usStr.set("")
        self.pwStr.set("")
        self.frame_manager.show_frame("main")

    def refresh(self):
        self.usStr.set("")
        self.pwStr.set("")
# </Login Frame>


# <Signup Frame>
class SignupFrame(ttk.Frame):
    def __init__(self, parent, frame_manager, app):
        super().__init__(parent)
        self.frame_manager = frame_manager
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        mainframe = ttk.Frame(self, padding="20 20 20 20")
        mainframe.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ttk.Label(mainframe, text="Crear Nuevo Usuario",
                  font=('Arial', 16, 'bold')).grid(row=0, columnspan=2, pady=20)

        ttk.Label(mainframe, text="Usuario").grid(
            row=1, column=0, sticky=W, pady=5)
        self.usStr = StringVar()
        ttk.Entry(mainframe, textvariable=self.usStr).grid(
            row=1, column=1, pady=5)

        ttk.Label(mainframe, text="Contraseña").grid(
            row=2, column=0, sticky=W, pady=5)
        self.pwStr = StringVar()
        ttk.Entry(mainframe, textvariable=self.pwStr,
                  show="*").grid(row=2, column=1, pady=5)

        ttk.Button(mainframe, text='Crear nuevo usuario',
                   command=self.try_new_user).grid(row=3, columnspan=2, pady=10)

        ttk.Button(mainframe, text="← Volver al inicio de sesión",
                   command=self.go_back).grid(row=4, columnspan=2, pady=10)

        self.bind("<Return>", lambda e: self.try_new_user())

    def try_new_user(self):
        givenUser = self.usStr.get()
        givenPassword = self.pwStr.get()

        if "," in givenPassword + givenUser:
            InformativeWindow(
                self, 'No incluya comas (",") en el usuario ni contraseña')
            return
        if db.getUserId(givenUser) is not None:
            InformativeWindow(self, "El usuario ya existe")
            return

        db.addUser(givenUser, givenPassword)

        # Automatically log in the new user
        userId = db.getUserId(givenUser)
        self.app.cUser = userId
        self.app.cAdmin = db.isAdmin(userId)

        self.usStr.set("")
        self.pwStr.set("")

        InformativeWindow(self, "Usuario creado exitosamente.")
        self.frame_manager.show_frame("main")

    def go_back(self):
        self.usStr.set("")
        self.pwStr.set("")
        self.frame_manager.show_frame("login")

    def refresh(self):
        self.usStr.set("")
        self.pwStr.set("")
# </Signup Frame>


# <Manage Bookings Frame>
class ManageBookingsFrame(ttk.Frame):
    def __init__(self, parent, frame_manager, app):
        super().__init__(parent)
        self.frame_manager = frame_manager
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        mainframe = ttk.Frame(self, padding="10 10 10 10")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ttk.Label(mainframe, text="Administrar Reservas",
                  font=('Arial', 16, 'bold')).grid(row=0, sticky=(W), pady=10)

        # Container for treeview
        tree_frame = ttk.Frame(mainframe)
        tree_frame.grid(row=1, column=0, sticky=(N, S, E, W))
        mainframe.rowconfigure(1, weight=1)
        mainframe.columnconfigure(0, weight=1)

        # Create treeview
        self.tree = ttk.Treeview(tree_frame, show="headings")

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=(N, S, E, W))
        vsb.grid(row=0, column=1, sticky=(N, S))
        hsb.grid(row=1, column=0, sticky=(E, W))

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Context menu
        self.menu = Menu(self.tree, tearoff=0)
        self.tree.bind("<Button-3>", self.show_menu)

        # Back button
        ttk.Button(mainframe, text="← Volver al menú principal",
                   command=self.go_back).grid(row=2, pady=10)

    def show_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            row_id = int(row_id)
            bkng = self.userBookings[row_id]
            self.menu.delete(0, "end")

            if bkng["state"] in (0, 1):
                if self.app.cAdmin:
                    self.menu.add_command(
                        label="Aceptar", command=lambda: self.aceptar(bkng["id"]))
                    self.menu.add_command(label="Rechazar",
                                          command=lambda: self.rechazar(bkng["id"]))
                elif bkng["state"] == 0:
                    self.menu.add_command(label="Cancelar",
                                          command=lambda: self.cancelar(bkng["id"]))

            self.menu.post(event.x_root, event.y_root)

    def cancelar(self, id):
        if confirmationWindow(self, "¿Está seguro de que desea cancelar su reserva? Esta acción no puede revertirse."):
            db.cancelBooking(id)
            self.refresh()

    def aceptar(self, id):
        db.acceptBooking(id)
        self.refresh()

    def rechazar(self, id):
        db.declineBooking(id)
        self.refresh()

    def go_back(self):
        self.frame_manager.show_frame("main")

    def refresh(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get bookings
        if self.app.cAdmin:
            self.userBookings = db.getAllBookings()
        else:
            self.userBookings = db.getUsersBookings(self.app.cUser)

        # Configure columns
        columns = ["username", "state", "names", "ages", "food",
                   "roomType", "startDate", "finishDate"]
        headings = ["Usuario", "Estado", "Personas", "Edades", "Comida",
                    "Tipo de habitación", "Fecha de inicio", "Fecha de finalización"]

        if not self.app.cAdmin:
            columns = columns[1:]
            headings = headings[1:]

        self.tree["columns"] = columns

        for i in range(len(headings)):
            self.tree.heading(i, text=headings[i])
            self.tree.column(i, width=120, anchor="center")

        # Insert data
        row = 0
        for bkng in formatBookings(self.userBookings):
            self.tree.insert("", END, iid=row, values=[
                bkng.get(col, "") for col in columns])
            row += 1
# </Manage Bookings Frame>


# <New Booking Frame>
class NewBookingFrame(ttk.Frame):
    def __init__(self, parent, frame_manager, app):
        super().__init__(parent)
        self.frame_manager = frame_manager
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Main scrollable container
        canvas = Canvas(self)
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Layout
        canvas.grid(row=0, column=0, sticky=(N, S, E, W))
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        mainframe = ttk.Frame(scrollable_frame, padding="10 10 10 10")
        mainframe.grid(row=0, column=0, sticky=(N, W, E, S))

        ttk.Label(mainframe, text="Nueva Reserva",
                  font=('Arial', 16, 'bold')).grid(row=0, columnspan=2, pady=10)

        # People section
        people_frame = ttk.LabelFrame(
            mainframe, text="Personas", padding="10 10 10 10")
        people_frame.grid(row=1, column=0, sticky=(W, E, N), padx=5, pady=5)

        ttk.Label(people_frame, text="Cantidad de personas:").pack()
        self.quant = IntVar(value=1)
        self.stored_q = -1
        q_entry = ttk.Entry(people_frame, textvariable=self.quant)
        q_entry.bind("<FocusOut>", self.update)
        q_entry.pack()

        self.q_warn = StringVar()
        ttk.Label(people_frame, textvariable=self.q_warn,
                  foreground="red").pack()

        self.nameNage = ttk.Frame(people_frame)
        self.nameNage.pack(padx=5, pady=5)

        self.NNA_warn = StringVar()
        self.names = [StringVar(value="") for _ in range(2)]
        self.ages = [IntVar(value=0) for _ in range(2)]
        self.NNA_wdgts = []

        ttk.Label(self.nameNage, text="Nombres:").grid(
            column=0, row=0, sticky=W)
        ttk.Label(self.nameNage, text="Edades:").grid(
            column=1, row=0, sticky=E)
        ttk.Label(self.nameNage, textvariable=self.NNA_warn,
                  foreground="red").grid(column=0, columnspan=2, row=6)

        # Room Type section
        room_frame = ttk.LabelFrame(
            mainframe, text="Habitación", padding="10 10 10 10")
        room_frame.grid(row=2, column=0, sticky=(W, E, N), padx=5, pady=5)

        ttk.Label(room_frame, text="Elegir habitación:").pack()
        self.selected_roomType = IntVar(value=-1)
        self.room_warn = StringVar()

        for size in [('Privado', 0), ('Compartido', 1)]:
            ttk.Radiobutton(room_frame, text=size[0], value=size[1],
                            variable=self.selected_roomType).pack(anchor="w", fill='x', padx=5, pady=2)

        ttk.Label(room_frame, textvariable=self.room_warn,
                  foreground="red").pack()

        # Food section
        food_frame = ttk.LabelFrame(
            mainframe, text="Comida", padding="10 10 10 10")
        food_frame.grid(row=1, column=1, sticky=(W, E, N), padx=5, pady=5)

        self.foodBool = BooleanVar()
        self.foodComment = StringVar()

        ttk.Label(food_frame,
                  text=f"¿Desea incluir desayuno?\nEl coste es de {FOOD_PRICE_PER_NIGHT} por noche",
                  wraplength=250).pack()
        ttk.Checkbutton(food_frame, variable=self.foodBool, text="Incluir desayuno",
                        onvalue=True, offvalue=False, command=self.summon_food).pack()

        self.foodLbl = ttk.Label(food_frame,
                                 text="Comentario sobre condiciones alimentarias:",
                                 wraplength=250)
        self.foodEntry = ttk.Entry(food_frame, textvariable=self.foodComment)

        # Dates section
        dates_frame = ttk.LabelFrame(
            mainframe, text="Fechas", padding="10 10 10 10")
        dates_frame.grid(row=2, column=1, rowspan=2,
                         sticky=(E, W, N), padx=5, pady=5)

        self.startDate = StringVar()
        self.finishDate = StringVar()
        self.startDate.set(date.today())
        self.finishDate.set(date.today())

        ttk.Label(dates_frame, text="Inicio").grid(row=0, column=0)
        ttk.Label(dates_frame, text="Fin").grid(row=0, column=1)

        self.startCalendar = tkcalendar.Calendar(
            dates_frame, mindate=date.today(), textvariable=self.startDate,
            locale="es", date_pattern="y-mm-dd")
        self.startCalendar.grid(row=1, column=0, padx=2)
        self.startCalendar.bind("<<CalendarSelected>>", self.update)

        self.finishCalendar = tkcalendar.Calendar(
            dates_frame, textvariable=self.finishDate,
            locale="es", date_pattern="y-mm-dd")
        self.finishCalendar.grid(row=1, column=1, padx=2)
        self.finishCalendar.bind("<<CalendarSelected>>", self.update)

        self.dates_warn = StringVar()
        ttk.Label(dates_frame, textvariable=self.dates_warn,
                  foreground="red").grid(row=2, column=0, columnspan=2)

        # Contact section
        contact_frame = ttk.LabelFrame(
            mainframe, text="Contacto", padding="10 10 10 10")
        contact_frame.grid(row=3, column=0, sticky=(W, E), padx=5, pady=5)

        self.contact = StringVar()
        ttk.Label(contact_frame,
                  text="Número de teléfono o correo electrónico:",
                  wraplength=250).pack()
        ttk.Entry(contact_frame, textvariable=self.contact).pack(fill='x')

        # Buttons
        button_frame = ttk.Frame(mainframe)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Reservar",
                   command=self.submit).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="← Volver",
                   command=self.go_back).pack(side=LEFT, padx=5)

        self.update()

    def update(self, event=None):
        if self.checkQuant():
            self.summon_people()
        self.checkNNA()
        self.summon_food()
        self.summon_dates()

    def checkQuant(self):
        try:
            q = self.quant.get()
            if q != self.stored_q:
                if q > 2 or q < 1:
                    self.q_warn.set("La cantidad debe ser de entre 1 y 2.")
                else:
                    self.q_warn.set("")
                    if self.stored_q != q:
                        self.stored_q = q
                        return True
        except TclError:
            self.q_warn.set("La cantidad debe ser un número.")
        return False

    def checkNNA(self, event=None):
        try:
            for a in self.ages:
                a.get()
            for n in self.names:
                n = n.get()
                if "," in n:
                    self.NNA_warn.set('No incluya comas (",")')
                    return
            self.NNA_warn.set("")
        except TclError:
            self.NNA_warn.set("Todas las edades deben ser números")

    def checkRoom(self):
        if self.selected_roomType.get() == -1:
            self.room_warn.set("Debe seleccionar una habitación")
        else:
            self.room_warn.set("")

    def checkConForm(self):
        con = self.contact.get().strip()
        numcon = without(con, (" ", "-", "+"))
        if numcon.isdigit() and len(numcon) == 10:
            return numcon
        elif re.match(r'^[^@]+@[^@]+\.[^@]+', con):
            return con
        else:
            return False

    def summon_people(self, event=None):
        q = self.quant.get()
        for w in self.NNA_wdgts:
            w.destroy()
        self.NNA_wdgts[:] = []

        for i in range(q):
            a = ttk.Entry(self.nameNage, textvariable=self.names[i])
            a.grid(column=0, row=i+2, sticky=(W, E), padx=2, pady=2)
            b = ttk.Entry(self.nameNage, textvariable=self.ages[i])
            b.grid(column=1, row=i+2, sticky=(W, E), padx=2, pady=2)
            self.NNA_wdgts.append(a)
            self.NNA_wdgts.append(b)

    def summon_food(self, event=None):
        if self.foodBool.get():
            self.foodLbl.pack()
            self.foodEntry.pack(fill='x')
        else:
            self.foodComment.set("")
            self.foodEntry.pack_forget()
            self.foodLbl.pack_forget()

    def summon_dates(self):
        try:
            sd = date.fromisoformat(self.startDate.get())
            fd = date.fromisoformat(self.finishDate.get())
            if sd > fd:
                self.dates_warn.set(
                    "La fecha de inicio no puede ser mayor a fecha de finalización")
            else:
                self.dates_warn.set("")
        except:
            self.dates_warn.set("Error en las fechas")

    def submit(self):
        self.update()
        self.checkRoom()

        if (self.NNA_warn.get() == self.dates_warn.get() ==
                self.room_warn.get() == self.q_warn.get() == ""):

            q = self.quant.get()
            foodAuxVar = self.foodBool.get()
            if foodAuxVar:
                foodAuxVar2 = self.foodComment.get()
                if foodAuxVar2 != "":
                    foodAuxVar = foodAuxVar2
                else:
                    foodAuxVar = 1
            else:
                foodAuxVar = 0

            namesAuxVar = []
            for n in self.names[:q]:
                n = n.get().strip()
                if n != "" and n is not None:
                    namesAuxVar.append(n)
                else:
                    self.NNA_warn.set('Deben ingresarse nombres')
                    return

            agesAuxVar = []
            for a in self.ages[:q]:
                a = a.get()
                if not a > 0:
                    self.NNA_warn.set('Todas las edades deben ser mayores a 0')
                    return
                if a > 0:
                    agesAuxVar.append(str(a))

            if not (contactData := self.checkConForm()):
                InformativeWindow(
                    self, 'Introduzca un número de 10 dígitos o correo electrónico válido\n' +
                    'Ejemplos: "123 456-7890", "name@email.net"')
                return

            sdate = date.fromisoformat(self.startDate.get())
            fdate = date.fromisoformat(self.finishDate.get())
            bkng = db.Booking(None, self.app.cUser, 0, self.foodBool.get(), foodAuxVar,
                              sdate, fdate, "comment", contactData, 0)
            tryNewBooking(bkng, [{age: int(age), name: name} for age, name in zip(
                agesAuxVar, namesAuxVar)], self.selected_roomType.get())
            InformativeWindow(self, "Reserva añadida")
            self.frame_manager.show_frame("main")
        else:
            InformativeWindow(self, "Debe completar los campos correctamente")

    def go_back(self):
        self.frame_manager.show_frame("main")

    def refresh(self):
        # Reset form
        self.quant.set(1)
        self.stored_q = -1
        for n in self.names:
            n.set("")
        for a in self.ages:
            a.set(0)
        self.selected_roomType.set(-1)
        self.foodBool.set(False)
        self.foodComment.set("")
        self.contact.set("")
        self.startDate.set(date.today())
        self.finishDate.set(date.today())
        self.q_warn.set("")
        self.NNA_warn.set("")
        self.room_warn.set("")
        self.dates_warn.set("")
        self.update()
# </New Booking Frame>


# <Application Class>
class HotelReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monjas - Sistema de Reservas")
        self.root.geometry("900x700")
        try:
            self.root.iconbitmap(r"icon.ico")
        except:
            pass  # Icon file not found

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Application state
        self.cUser = 0
        self.cAdmin = 0

        # Initialize frame manager
        self.frame_manager = FrameManager(root)

        # Create all frames
        self.main_frame = MainMenuFrame(root, self.frame_manager, self)
        self.login_frame = LoginFrame(root, self.frame_manager, self)
        self.signup_frame = SignupFrame(root, self.frame_manager, self)
        self.bookings_frame = ManageBookingsFrame(
            root, self.frame_manager, self)
        self.new_booking_frame = NewBookingFrame(
            root, self.frame_manager, self)

        # Register frames
        self.frame_manager.add_frame("main", self.main_frame)
        self.frame_manager.add_frame("login", self.login_frame)
        self.frame_manager.add_frame("signup", self.signup_frame)
        self.frame_manager.add_frame("bookings", self.bookings_frame)
        self.frame_manager.add_frame("new_booking", self.new_booking_frame)

        # Start with main menu
        self.frame_manager.show_frame("main")
# </Application Class>


# <Main Entry Point>
if __name__ == "__main__":
    # Initialize database
    db.initdb()

    # Create and run application
    root = Tk()
    app = HotelReservationApp(root)
    root.mainloop()
# </Main Entry Point>
