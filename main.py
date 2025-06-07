try:
    import os
    from tkinter import *
    from tkinter import ttk
    import csv
    import copy
    from datetime import date
except ModuleNotFoundError:
    print("One or more modules not found")
    print("Aborting...")
    raise SystemExit
# date.today()
os.system("cls")

# <defs:


def modifyCsvRow(filepath, newValue, rowI=None, conditionField=None, conditionValue=None, field=None):
    tPath = "temp_" + filepath
    with open(filepath, 'r', encoding='utf-8') as inp, open(tPath, 'w', encoding='utf-8', newline='') as out:
        reader = list(csv.DictReader(inp))
        writer = csv.DictWriter(
            out, fieldnames=reader[0].keys())
        if conditionField is None and conditionValue is None and rowI:
            if field is None:
                reader[rowI] = newValue
            else:
                reader[rowI][field] = newValue
        elif rowI is None and conditionField and conditionValue:
            for row in reader:
                if row[conditionField] == str(conditionValue):
                    if field is None:
                        row = newValue
                    else:
                        row[field] = newValue
        else:
            print(
                f"Couldn't resolve modifyCsvRow(filepath={filepath}, newValue={newValue}, rowI={rowI},conditionField={conditionField}, conditionValue={conditionValue}, field={field}) as both or nor row identifier and condition identifier were provided.")

        writer.writeheader()
        writer.writerows(reader)

    os.replace(tPath, filepath)


def upUsers():
    global us
    with open("users.csv", "r", encoding='utf8', newline="",) as csvfile:
        us = list(csv.DictReader(csvfile))
        for u in us:
            u["admin"] = bool(int(u["admin"]))


def upReservas():
    global bookings
    with open("reservas.csv", "r", encoding='utf8', newline="") as csvfile:
        bookings = list(csv.DictReader(csvfile))
        for bkng in bookings:
            bkng["id"] = int(bkng["id"])
            bkng["state"] = int(bkng["state"])
            bkng["names"] = bkng["names"].split(";")
            bkng["ages"] = bkng["ages"].split(";")
            bkng["roomType"] = int(bkng["roomType"])


def updateFiles():
    upReservas()
    upUsers()


def addCsv(filepath, *args):
    with open(filepath, "a", encoding='utf8') as w:
        list = []
        for arg in args:
            list.append(str(arg))
        w.write("\n" + ",".join(list))
    upUsers()
    upReservas()


def indexOfUser(user):
    try:
        return next(i for i, a in enumerate(us) if a["username"] == user)
    except ValueError:
        print("no está el usuario")
        return None


def getResrevas(user):
    global bookings
    return [bkng for bkng in bookings if bkng.get("username") == user]


def tkWindow(title, grid=True, geometry="0x0", resizable: bool = False):
    a = Tk()
    if resizable == True:
        a.resizable(False, False)
    else:
        a.resizable(True, True)
    a.title(title)
    a.iconbitmap(r"icon.ico")
    if grid:
        a.columnconfigure(0, weight=1)
        a.rowconfigure(0, weight=1)
    if geometry != "0x0":
        a.geometry(geometry)
    return a


def logInWindow():
    def checkUsPw(event=""):
        global cUser, us
        givenUser = usStr.get()
        givenPassword = pwStr.get()
        userIdx = indexOfUser(givenUser)
        print(us[userIdx]["password"])
        if userIdx != None:
            if givenPassword == us[userIdx]["password"]:
                cUser = us[userIdx]["username"]
                logIn(cUser, userIdx)
                uspw.destroy()
            else:
                InformativeWindow("Contraseña incorrecta. Intente nuevamente")
        else:
            # inputs quiere nuevo usuario?
            if confirmationWindow(
                    "Usuario no encntrado. ¿Quiere crear un nuevo usuario?"):
                newUserWindow()

    uspw = tkWindow("Iniciar sesión", geometry=("300x300"))

    mainframe = ttk.Frame(uspw, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

    usStr = StringVar(mainframe)
    pwStr = StringVar(mainframe)

    ttk.Label(mainframe, text="Usuario").pack()
    ttk.Entry(mainframe, textvariable=usStr).pack()
    ttk.Label(mainframe, text="Contraseña").pack()
    ttk.Entry(mainframe, textvariable=pwStr, show="*").pack()
    ttk.Button(mainframe, text='Iniciar sesión',
               command=checkUsPw).pack(pady=10)
    ttk.Button(mainframe, text="¿Primera vez? Cree unnuevo usuario",
               command=newUserWindow).pack()
    uspw.bind("<Return>", checkUsPw)


def logIn(user, userIdx):
    global cUser, cAdmin, us
    cUser = user
    if us[userIdx]["admin"]:
        cAdmin = 1
    else:
        cAdmin = 0
    print("iniciaste sesión como " + cUser)
    logInBtt.grid_forget()
    bkgsBtt.grid()
    signOutBtt.grid()
    welcomeMsg.set("Bienvenido, " + cUser)


def signOut():
    global cUser
    cUser = ""
    signOutBtt.grid_forget()
    bkgsBtt.grid_forget()
    logInBtt.grid()
    welcomeMsg.set("Bienvenido")


def newUserWindow():
    def tryNewUs(*args):
        givenUser = usStr.get()
        givenPassword = pwStr.get()
        if indexOfUser(givenUser) == None:
            addCsv("users.csv", givenUser, givenPassword, 0)
            InformativeWindow("Usuario creado. Inicie sesión ahora.")
            newUsw.destroy()
        else:
            InformativeWindow("El usuario ya existe")

    newUsw = tkWindow("Crear nuevo usuario", geometry="300x300")
    mainframe = ttk.Frame(newUsw, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    usStr = StringVar(mainframe)
    pwStr = StringVar(mainframe)
    ttk.Label(mainframe, text="Usuario").pack()
    ttk.Entry(mainframe, textvariable=usStr).pack()
    ttk.Label(mainframe, text="Contraseña").pack()
    ttk.Entry(mainframe, textvariable=pwStr, show="*").pack()
    ttk.Button(mainframe, text='Crear nuevo usuario', command=tryNewUs).pack()
    newUsw.bind("<Return>", tryNewUs)


def ManageBookingsWindow():
    global cUser, cAdmin

    def cancel(i, f):
        if confirmationWindow("¿Está seguro de que desea cancelar su reserva? Esta acción no puede revertirse."):
            # modifyCsvRow("reservas.csv", i, field="state", newValue=3)
            for w in f.winfo_children():
                if int(w.grid_info().get("column", -1)) == f:
                    w.destroy()

    def aceptar(i):
        modifyCsvRow("reservas.csv", i, field="state", newValue=1)

    def rechazar(i):
        modifyCsvRow("reservas.csv", i, field="state", newValue=3)

    bw = tkWindow("Administrar reservas")
    mainframe = ttk.Frame(bw, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    if cAdmin:
        userBookings = bookings
    else:
        userBookings = getResrevas(cUser)
    dataGrid = Frame(mainframe)
    dataGrid.pack()
    i = 0
    for bkng in userBookings:
        print(bkng)
        row = i
        # i2 is i for elements of b
        clmn = 0
        for a in bkng.values():
            # Create labels only for third and following elements of b
            if clmn >= 2:
                l = Label(dataGrid, text=a, wraplength=200)
                l.grid(row=row, column=clmn, padx=10, pady=20)
                if bkng["state"] == 3:
                    l.config(bg="red", fg="white")
            clmn += 1
        if cAdmin or bkng["state"] == 0:
            opts = ttk.Menubutton(dataGrid, text="Opciones")
            opts.grid(row=row, column=clmn, padx=10)

            # Set `tearoff=0` to remove the dashed line
            menu = Menu(dataGrid, tearoff=0)
            opts["menu"] = menu  # Link the menu to the Menubutton

            # Add options to the menu with commands
            if bkng["state"] == 0:
                # Cancelar: enviando el id de la reserva, que está en la posición 0 de a
                menu.add_command(label="Cancelar",
                                 command=lambda: cancel(bkng["id"], row))
                # only available if not yet accepted:
                if not cAdmin:
                    menu.add_command(label="Modificar",
                                     command=lambda: BookingWindow(modify=bkng["id"]))
            if cAdmin:
                menu.add_command(
                    label="Aceptar", command=lambda: aceptar(bkng["id"]))
                menu.add_command(label="Rechazar",
                                 command=lambda: rechazar(bkng["id"]))
        i += 1

    headings = ("Personas", "Edades", "Comida", "Tipo de habitación",
                "Fecha de inicio", "Fecha de finalización")
    columns = ("names", "ages", "food", "roomType", "startDate", "finishDate")

    tree = ttk.Treeview(mainframe, columns=columns, show="headings")
    for i in range(len(headings)):
        tree.heading(i, text=headings[i])
        tree.column(i, width=100, anchor="center")

    for bkng in userBookings:
        tree.insert("", END, values=[bkng.get(col, "") for col in columns])

    tree.pack(expand=True, fill="both")


def BookingWindow(modify=False):
    global cUSer, bookings

    def submit():
        print("should submit")

    def update(event=""):
        summon_people()
        summon_roomType()
        summon_food()

    def checkNNA(event=""):
        try:
            for a in ages:
                a.get()
            NNA_warn.set("")
        except TclError:
            NNA_warn.set("Todas las edades deben ser números.")

    def summon_roomType(event=""):
        for w in roomRB.winfo_children():
            w.destroy()

        roomTypes = []
        q = quant.get()
        if q == 1:
            roomTypes = [('Privado Simple', 0), ('Compartido Simple', 2)]
        elif q == 2:
            roomTypes = [('Privado Doble', 1), ('Compartido doble', 3)]
        for size in roomTypes:
            r = ttk.Radiobutton(
                roomRB,
                text=size[0],
                value=size[1],
                variable=selected_roomType
            )
            r.pack(anchor="w", fill='x', padx=5, pady=5)

    def summon_people(event=""):
        try:
            q = quant.get()
            if q > 2 or q < 1:
                q_warn.set("La cantidad debe ser de entre 1 y 2 personas.")
                return
            else:
                q_warn.set("")
        except TclError:
            q_warn.set("La cantidad debe ser un número.")
            return
        for w in NNA_wdgts:
            w.destroy()
        NNA_wdgts[:] = []
        for i in range(q):
            a = ttk.Entry(nameNage, textvariable=names[i])
            a.grid(column=0, row=i+2, sticky=(W, E))
            b = ttk.Entry(nameNage, textvariable=ages[i])
            b.grid(column=1, row=i+2, sticky=(W, E))
            NNA_wdgts.append(a)
            NNA_wdgts.append(b)
        nameNage.bind("<Return>", checkNNA)
        checkNNA()

    def summon_food(event=""):
        if foodBool.get():
            foodLbl.pack()
            foodEntry.pack()
            foodComment.set("")
        else:
            foodEntry.forget()
            foodLbl.forget()

    bw = tkWindow("Nueva reserva")
    if modify != False:
        bw.title("Modificar reserva")
    #
    # people
    people = ttk.Frame(bw)
    people.grid(column=0, row=0, sticky=(E, N, W))
    ttk.Label(people, text="Cantidad de personas:").pack()

    quant = IntVar(people, value=1)
    q_entry = ttk.Entry(people, textvariable=quant)
    q_entry.bind("<Return>", update)
    q_entry.bind("<FocusOut>", update)
    q_entry.pack()
    q_warn = StringVar(people)
    ttk.Label(people, textvariable=q_warn, foreground="red").pack()

    NNA_wdgts = []
    nameNage = ttk.Frame(people)
    nameNage.bind("<FocusOut>", update)
    nameNage.pack(padx=5, pady=5)
    NNA_warn = StringVar(nameNage)
    names = [StringVar(nameNage) for _ in range(4)]
    ages = [IntVar(nameNage) for _ in range(4)]
    ttk.Label(nameNage, text="Nombres:").grid(
        column=0, row=0, sticky=(W, N))
    ttk.Label(nameNage, text="Edades:").grid(
        column=1, row=0, sticky=(E, N))
    ttk.Label(nameNage, textvariable=NNA_warn,
              foreground="red").grid(column=1, row=6)

    #
    # roomType
    roomType = ttk.Frame(bw)
    roomType.grid(column=0, row=1, sticky=(S, W, E), padx=5, pady=5)
    ttk.Label(roomType, text="Elegir habitación:").pack()

    roomRB = ttk.Frame(roomType)
    roomRB.bind("<FocusOut>", update)
    roomRB.pack(fill="x", padx=5, pady=5)

    selected_roomType = StringVar(roomRB)

    #
    # food
    food = ttk.Frame(bw)
    food.grid(column=1, row=0, sticky=(N, E, W))
    foodBool = BooleanVar(food)
    foodComment = StringVar()
    ttk.Label(food, text="¿Desea incluir desayuno? El coste es de").pack()
    ttk.Checkbutton(food, variable=foodBool, text="Incluir desayuno",
                    onvalue=True, offvalue=False, command=summon_food).pack()
    foodLbl = ttk.Label(
        food, text="Si desea incluir algún comentario sobre alguna condición que deba incluir la comida que se le brinde, hágalo aquí:", wraplength=180)
    foodEntry = ttk.Entry(food, textvariable=foodComment)

    food.bind("<Return>", update)
    food.bind("<FocusOut>", update)
    foodEntry.bind("<Return>", update)
    foodEntry.bind("<FocusOut>", update)

    #
    # dates
    dates = ttk.Frame(bw)
    dates.grid(column=1, row=1, sticky=(W, S, E))

    startDate = StringVar(dates)
    finishDate = StringVar(dates)

    # Year Dropdown
    years = [str(year) for year in range(1900, 2100)]
    year_combobox = ttk.Combobox(dates, values=years, state="readonly")
    year_combobox.set("Select Year")
    year_combobox.pack(pady=5)

    # Month Dropdown
    months = [str(month) for month in range(1, 13)]
    month_combobox = ttk.Combobox(dates, values=months, state="readonly")
    month_combobox.set("Select Month")
    month_combobox.pack(pady=5)

    # Day Dropdown
    days = [str(day) for day in range(1, 32)]
    day_combobox = ttk.Combobox(dates, values=days, state="readonly")
    day_combobox.set("Select Day")
    day_combobox.pack(pady=5)

    ttk.Button(bw, text="Reservar", width=25, command=submit).grid(
        row=2, column=0, columnspan=2, sticky=(S), pady=5, padx=5)
    update()


def confirmationWindow(msg):
    result = {'value': None}

    def yBtt():
        result['value'] = True
        confw.destroy()

    def nBtt():
        result['value'] = False
        confw.destroy()

    confw = tkWindow(msg)

    mainframe = ttk.Frame(confw, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=N)

    ttk.Label(mainframe, text=msg).grid(row=0, sticky=(W, S, E))
    ttk.Button(mainframe, text="Sí", command=yBtt).grid(
        column=0, row=1, sticky=(W, S), pady=10)
    ttk.Button(mainframe, text="No", command=nBtt).grid(
        column=1, row=1, sticky=(E, S), pady=10)
    confw.grab_set()
    confw.wait_window()

    return result['value']


def InformativeWindow(msg):
    infw = tkWindow(msg, grid=False)
    Label(infw, text=msg).pack()
    ttk.Button(infw, text="Ok", command=lambda: infw.destroy()).pack()
    infw.grab_set()
    infw.wait_window()


# defs>
# <setup
us = []

bookings = []
bookingsByUser = []
updateFiles()

root = tkWindow("Monjas", geometry="650x350")

welcomeMsg = StringVar()
welcomeMsg.set("Bienvenido")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=N)
mainframe.grid_columnconfigure(0, weight=1)
ttk.Label(mainframe, textvariable=welcomeMsg).grid(row=0, sticky=(W, S, E))
logInBtt = ttk.Button(mainframe,
                      text="Iniciar sesión",
                      command=logInWindow)
logInBtt.grid(row=1, sticky=(W, S, E), pady=10)
signOutBtt = ttk.Button(mainframe,
                        text="Cerrar sesión",
                        command=signOut)
signOutBtt.grid(row=1, sticky=(W, E), pady=10)
signOutBtt.grid_forget()
bkgsBtt = ttk.Button(mainframe,
                     text="Administrar reservas",
                     command=ManageBookingsWindow)
bkgsBtt.grid(row=3, sticky=(W, E), pady=10)
bkgsBtt.grid_forget()

# setup>

# #1: user select:
givenUser = ""
givenPassword = ""
cUser = ""
cAdmin = 0

# test:
BookingWindow()
cUser = "hacker"
ManageBookingsWindow()


root.mainloop()

# #2.1: user administrar reservas:
# show-matchingReservas
# #2.2: user crear reserva:
# ##inputs cPersonas nombres, edad, comida, habitación, startDate, finishDate, contacto, comment
# cPersonas = 2
# nombres = ["Lorenzo Sánchez", "Ismalol Hayno"]
# edades = ["18", "17"]
# comida = 0
# hab = 3
# startDate = "2024-05-25"
# finishDate = "2024-05-26"
# contacto = "+5493512297549"
# comment = "son negros"
#
# addCsv(
#    "reservas.csv",
#    len(bookings)
#    cUser,
#    "0",
#    ";".join(nombres),
#    ";".join(edades),
#    comida,
#    hab,
#    startDate,
#    finishDate,
#    contacto,
#    comment,
# )

# import user/password from csv
# import reservas from csv
# 1: iniciar sesión (admin/user)
# 2-admin: aceptar o rechazar reservas, administrar reservas
# 2-user: reservar / cancelar (administrar reservas propias)
#
# un mensaje "* perdiste treinta mil dólares *"
# datos = [reserva[id,usuario,estado de la reserva (0=por aceptar 1=aceptada/en espera, 2=terminada, 3=cancelada),
# nombres, edad, comida (0=sin 1=con "string/comentario"=dieta específica),
# tipo de habitación (0=privado simple, 1=privado doble, 2=compartido simple, 3=compartido doble)
# startDate, finishDate (ambos incluyente),
# persona de referencia/contacto, comentario]]
#
# Habitaciones:
# 24 total:
# Baño privado simple: $40 000
# Baño privado doble: $30 000
# 7 total:
# Baño compartido simple: $18 000
# Baño compartido doble: $15 000
