try:
    import os
    from tkinter import *
    from tkinter import ttk
    import csv
    import copy
    from datetime import date, datetime
except ModuleNotFoundError:
    print("One or more modules not found.\nAborting...")
    raise SystemExit
# date.today()
os.system("cls")

# <consts:
MAX_YEAR = date.today().year+5
MAX_ROOMS = 48
FOOD_PRICE_PER_NIGHT = 5000
ROOM_PRICE_PER_NIGHT = (60000, 85000, 50000, 55000)
# consts>

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
    updateFiles()


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
    with open(filepath, "a", encoding='utf8') as a:
        a.write(",".join([str(a) for a in args])+"\n")
    updateFiles()


def indexOfUser(user):
    try:
        return next((i for i, a in enumerate(us) if a["username"] == user), None)
    except ValueError:
        return None


def getResrevas(user):
    global bookings
    return [bkng for bkng in bookings if bkng.get("username") == user]


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
            b["roomType"] = "Privado simple"
        elif b["roomType"] == 1:
            b["roomType"] = "Privado doble"
        elif b["roomType"] == 2:
            b["roomType"] = "Compartido simple"
        elif b["roomType"] == 3:
            b["roomType"] = "Compartido doble"
        # startDate:
        # finishDate:
    return a


def tkWindow(title, grid=True, geometry=None, resizable: bool = False):
    a = Tk()
    if resizable == True:
        a.resizable(True, True)
    else:
        a.resizable(False, False)
    a.title(title)
    a.iconbitmap(r"icon.ico")
    if geometry is not None:
        a.geometry(geometry)
    if grid:
        a.columnconfigure(0, weight=1)
        a.rowconfigure(0, weight=1)
    return a


def logIn(user, userId):
    global cUser, cAdmin, us
    cUser = user
    if us[userId]["admin"]:
        cAdmin = 1
    else:
        cAdmin = 0
        newbkgBtt.grid()
    print("iniciaste sesión como " + cUser)
    logInBtt.grid_forget()
    bkgsBtt.grid()
    signOutBtt.grid()
    welcomeMsg.set("Bienvenido, " + cUser)


def logOut():
    global cUser
    cUser = ""
    signOutBtt.grid_forget()
    bkgsBtt.grid_forget()
    newbkgBtt.grid_forget()
    logInBtt.grid()
    welcomeMsg.set("Bienvenido")


def logInWindow():
    def checkUsPw(event=""):
        global cUser, us
        givenUser = usStr.get()
        givenPassword = pwStr.get()
        if "," in givenPassword+givenUser:
            InformativeWindow(
                'No incluya comas (",") en el usuario ni contraseña')
        else:
            userId = indexOfUser(givenUser)
            if userId != None:
                if givenPassword == us[userId]["password"]:
                    cUser = us[userId]["username"]
                    logIn(cUser, userId)
                    uspw.destroy()
                else:
                    InformativeWindow(
                        "Contraseña incorrecta. Intente nuevamente")
            else:
                # inputs quiere nuevo usuario?
                if confirmationWindow("Usuario no encontrado. ¿Quiere crear un nuevo usuario?"):
                    newUserWindow()
    uspw = tkWindow("Iniciar sesión", grid=True, geometry="300x300")

    usStr = StringVar(uspw)
    pwStr = StringVar(uspw)

    ttk.Label(uspw, text="Usuario").pack()
    ttk.Entry(uspw, textvariable=usStr).pack()
    ttk.Label(uspw, text="Contraseña").pack()
    ttk.Entry(uspw, textvariable=pwStr, show="*").pack()
    ttk.Button(uspw, text='Iniciar sesión',
               command=checkUsPw).pack(pady=10)
    ttk.Button(uspw, text="¿Primera vez? Cree un nuevo usuario",
               command=newUserWindow).pack()
    uspw.bind("<Return>", checkUsPw)


def newUserWindow():
    def tryNewUs(*args):
        givenUser = usStr.get()
        givenPassword = pwStr.get()
        if "," in givenPassword+givenUser:
            newUsw.wait_window(InformativeWindow(
                'No incluya comas (",") en el usuario ni contraseña'))
        else:
            if indexOfUser(givenUser) == None:
                addCsv("users.csv", givenUser, givenPassword, 0)
                InformativeWindow("Usuario creado. Inicie sesión ahora.")
                newUsw.destroy()
            else:
                InformativeWindow("El usuario ya existe")

    newUsw = tkWindow("Crear nuevo usuario", grid=True, geometry="300x300")
    usStr = StringVar(newUsw)
    pwStr = StringVar(newUsw)
    ttk.Label(newUsw, text="Usuario").pack()
    ttk.Entry(newUsw, textvariable=usStr).pack()
    ttk.Label(newUsw, text="Contraseña").pack()
    ttk.Entry(newUsw, textvariable=pwStr, show="*").pack()
    ttk.Button(newUsw, text='Crear nuevo usuario',
               command=tryNewUs).pack(pady=10)
    newUsw.bind("<Return>", tryNewUs)


def ManageBookingsWindow():
    global cUser, cAdmin

    def cancelar(id):
        if confirmationWindow("¿Está seguro de que desea cancelar su reserva? Esta acción no puede revertirse."):
            modifyCsvRow("reservas.csv", newValue=3,
                         conditionField="id", conditionValue=id, field="state")

    def aceptar(id):
        modifyCsvRow("reservas.csv", conditionField="id",
                     conditionValue=id, field="state", newValue=1)

    def rechazar(id):
        modifyCsvRow("reservas.csv", conditionField="id",
                     conditionValue=id, field="state", newValue=3)

    def modify(id):

        bw.wait_window(BookingWindow(modify=id))

    def show_menu(event):
        row_id = tree.identify_row(event.y)
        if row_id:
            row_id = int(row_id)
            bkng = userBookings[row_id]
            menu.delete(0, "end")
            # only available if not yet accepted:
            if bkng["state"] in (0, 1):
                if cAdmin:
                    menu.add_command(
                        label="Aceptar", command=lambda: aceptar(bkng["id"]))
                    menu.add_command(label="Rechazar",
                                     command=lambda: rechazar(bkng["id"]))
                elif bkng["state"] == 0:
                    menu.add_command(label="Cancelar",
                                     command=lambda: cancelar(bkng["id"]))
                    menu.add_command(label="Modificar",
                                     command=lambda: modify(bkng["id"]))
            menu.post(event.x_root, event.y_root)

    bw = tkWindow("Administrar reservas")
    mainframe = ttk.Frame(bw, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    if cAdmin:
        userBookings = bookings
    else:
        userBookings = getResrevas(cUser)

    columns = ("state", "names", "ages", "food",
               "roomType", "startDate", "finishDate")
    headings = ("Estado", "Personas", "Edades", "Comida", "Tipo de habitación",
                "Fecha de inicio", "Fecha de finalización")
    tree = ttk.Treeview(mainframe, columns=columns, show="headings")
    for i in range(len(headings)):
        tree.heading(i, text=headings[i])
        tree.column(i, width=100, anchor="center")

    menu = Menu(tree, tearoff=0)

    row = 0
    for bkng in formatBookings(userBookings):
        tree.insert("", END, iid=row, values=[
                    bkng.get(col, "") for col in columns])
        row += 1

    tree.pack(expand=True, fill="both")
    tree.bind("<Button-3>", show_menu)


def BookingWindow(modify=False):
    global cUSer, bookings

    def submit():
        update()
        checkRoom()

        if (NNA_warn.get() == dates_warn.get() == room_warn.get() == q_warn.get() == ""):
            q = quant.get()
            foodAuxVar = foodBool.get()
            if foodAuxVar:
                foodAuxVar2 = foodComment.get()
                if foodAuxVar2 != "":
                    foodAuxVar = foodAuxVar2
                else:
                    foodAuxVar = 1
            else:
                foodAuxVar = 0

            namesAuxVar = []
            for n in names[:q]:
                n = n.get().strip()
                if n != "" and n is not None:
                    namesAuxVar.append(n)
                else:
                    NNA_warn.set('Deben ingresarse nombres')
                    return

            agesAuxVar = []
            for a in ages[:q]:
                a = a.get()
                if not a > 0:
                    NNA_warn.set('Todas las edades deben ser mayores a 0')
                    return
                if a > 0:
                    agesAuxVar.append(str(a))

            for v in vars:
                try:
                    startDate = date(
                        int(startYear.get()),
                        int(startMonth.get()),
                        int(startDay.get()))
                    finishDate = date(
                        int(finishYear.get()),
                        int(finishMonth.get()),
                        int(finishDay.get()))
                except ValueError:
                    dates_warn.set("Seleccione fechas")
                    return

            addCsv("reservas.csv",
                   len(bookings),
                   cUser,
                   0,
                   ";".join(namesAuxVar),
                   ";".join(agesAuxVar),
                   foodAuxVar,
                   selected_roomType.get(),
                   startDate,
                   finishDate)
            InformativeWindow("Reserva añadida")
            bw.destroy()
        else:
            InformativeWindow("Debe completar los campos correctamente")

    def update(event=""):
        if checkQuant():
            summon_people()
            summon_roomType()
        checkNNA()
        summon_food()
        summon_dates()

    def checkNNA(event=""):
        try:
            for a in ages:
                a = a.get()
            for n in names:
                n = n.get()
                if "," in n:
                    NNA_warn.set('No incluya comas (",")')
                    return
            NNA_warn.set("")
        except TclError:
            NNA_warn.set("Todas las edades deben ser números")

    def checkQuant():
        nonlocal stored_q
        try:
            q = quant.get()
            if q != stored_q:
                if q > 2 or q < 1:
                    q_warn.set("La cantidad debe ser de entre 1 y 2.")
                else:
                    q_warn.set("")
                    if stored_q != q:
                        stored_q = q
                        return True
        except TclError:
            q_warn.set("La cantidad debe ser un número.")
        return False

    def checkRoom():
        if selected_roomType.get() == -1:
            room_warn.set("Debe seleccionar una habitación")
        else:
            room_warn.set("")

    def summon_people(event=""):
        q = quant.get()
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

    def summon_food(event=""):
        if foodBool.get():
            foodLbl.pack()
            foodEntry.pack()
        else:
            foodComment.set("")
            foodEntry.forget()
            foodLbl.forget()

    def summon_dates():
        for i, v in enumerate(vars):
            l = limitvars[i]
            if v["y"].get() == str(date.today().year):
                l["minm"] = date.today().month
                if v["m"].get() == str(date.today().month):
                    l["mind"] = date.today().day
                else:
                    l["mind"] = 1
            else:
                l["minm"] = 1

            if v["m"].get() in (str(a) for a in (1, 3, 5, 7, 8, 10, 12)):
                l["maxd"] = 31
            elif v["m"].get() in (str(a) for a in (4, 6, 9, 11)):
                l["maxd"] = 30
            elif v["m"].get() == str(2):
                try:
                    datetime.strptime('Feb 29', v["y"].get())
                    l["maxd"] = 29
                except ValueError:
                    l["maxd"] = 28
            if (i == 1):
                l["miny"] = startYear.get()
                if startYear.get() == finishYear.get():
                    try:
                        l["minm"] = int(startMonth.get())
                        if startMonth.get() == finishMonth.get():
                            l["mind"] = int(startDay.get())
                    except ValueError:
                        pass

            # Now update
            comoboxes[i]["y_c"].config(values=[y for y in range(
                date.today().year, date.today().year+5)])
            comoboxes[i]["m_c"].config(
                values=[m for m in range(l["minm"], 13)])
            comoboxes[i]["d_c"].config(
                values=[d for d in range(l["mind"], l["maxd"]+1)])
        try:
            if int(startYear.get()) > int(finishYear.get()):
                dates_warn.set(
                    "Año de inicio no debe ser mayor a año de finalización")
                return
            elif int(startYear.get()) == int(finishYear.get()):
                if int(startMonth.get()) > int(finishMonth.get()):
                    dates_warn.set(
                        "Mes de inicio no debe ser mayor a mes de finalización")
                    return
                elif int(startMonth.get()) == int(finishMonth.get()):
                    if int(startDay.get()) > int(finishDay.get()):
                        dates_warn.set(
                            "Día de inicio no debe ser mayor a día de finalización")
                        return
            dates_warn.set("")
        except ValueError:
            pass

    bw = tkWindow("Nueva reserva")
    #
    # people
    people = ttk.Frame(bw)
    people.grid(column=0, row=0, sticky=(E, N, W))
    ttk.Label(people, text="Cantidad de personas:").pack()

    quant = IntVar(people, value=1)
    stored_q = -1
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
    names = [StringVar(nameNage, value="") for _ in range(2)]
    ages = [IntVar(nameNage, value=0) for _ in range(2)]
    ttk.Label(nameNage, text="Nombres:").grid(
        column=0, row=0, sticky=(W, N))
    ttk.Label(nameNage, text="Edades:").grid(
        column=1, row=0, sticky=(E, N))
    ttk.Label(nameNage, textvariable=NNA_warn,
              foreground="red").grid(column=0, columnspan=2, row=6)

    #
    # roomType
    roomType = ttk.Frame(bw)
    roomType.grid(column=0, row=1, sticky=(S, W, E), padx=5, pady=5)
    
    ttk.Label(roomType, text="Elegir habitación:").pack()
    roomRB = ttk.Frame(roomType)
    roomRB.bind("<FocusOut>", update)
    roomRB.pack(fill="x", padx=5, pady=5)
    selected_roomType = IntVar(roomRB, value=-1)
    room_warn = StringVar(roomRB)
    
    for size in [('Privado', 0), ('Compartido', 1)]:
            selected_roomType.set(-1)
    ttk.Label(roomRB, textvariable=room_warn, foreground="red").pack()

    #
    # food
    food = ttk.Frame(bw)
    food.grid(column=1, row=0, sticky=(N, E, W))
    foodBool = BooleanVar(food)
    foodComment = StringVar(food)
    ttk.Label(
        food, text=f"¿Desea incluir desayuno? El coste es de {FOOD_PRICE_PER_NIGHT} por noche", wraplength=150).pack()
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
    startYear = StringVar(dates)
    startMonth = StringVar(dates)
    startDay = StringVar(dates)
    finishYear = StringVar(dates)
    finishMonth = StringVar(dates)
    finishDay = StringVar(dates)

    vars = ({"y": startYear, "m": startMonth, "d": startDay},
            {"y": finishYear, "m": finishMonth, "d": finishDay})
    minStartMonth = minStartDay = minFinishYear = minFinishMonth = minFinishtDay = maxStartDay = maxFinishDay = 1
    limitvars = ({"minm": minStartMonth, "mind": minStartDay, "maxd": maxStartDay},
                 {"miny": minFinishYear, "minm": minFinishMonth, "mind": minFinishtDay, "maxd": maxFinishDay})
    labels = (("Año de inicio", "Mes de inicio", "Día de inicio"),
              ("Año de finalización", "Mes de finalización", "Día de finalización"))
    comoboxes = [{}, {}]

    for i in range(len(vars)):
        comoboxes[i] = dict(zip(["y_c", "m_c", "d_c"], [
                            ttk.Combobox(dates, state="readonly") for _ in range(3)]))
        for j, w in enumerate(vars[i].values()):
            c = list(comoboxes[i].values())[j]
            c.config(textvariable=w)
            c.set(labels[i][j])
            c.grid(pady=5, row=i, column=j)
            c.bind("<1>", update)
            c.bind("<Return>", update)

    dates_warn = StringVar(dates)
    ttk.Label(dates, textvariable=dates_warn, foreground="red").grid(
        column=0, row=2, columnspan=3)

    submitBtt = ttk.Button(bw, text="Reservar", width=25, command=submit).grid(
        row=2, column=0, columnspan=2, sticky=(S), pady=5, padx=5)

    if modify != False:
        bw.title("Modificar reserva")
        submitBtt.config(text="Modificar reserva")

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
    infw.grab_set()
    infw.focus_set()


# defs>

# <setup
us = []

bookings = []
updateFiles()

root = tkWindow("Monjas", geometry="650x350", resizable=True)

welcomeMsg = StringVar()
welcomeMsg.set("Bienvenido")

uspw = ttk.Frame(root, padding="3 3 12 12")
uspw.pack()
ttk.Label(uspw, textvariable=welcomeMsg).grid(row=0, sticky=(W, S, E))
logInBtt = ttk.Button(uspw,
                      text="Iniciar sesión",
                      command=logInWindow)
logInBtt.grid(row=1, sticky=(W, S, E), pady=10)
signOutBtt = ttk.Button(uspw,
                        text="Cerrar sesión",
                        command=logOut)
signOutBtt.grid(row=1, sticky=(W, E), pady=10)
signOutBtt.grid_forget()
bkgsBtt = ttk.Button(uspw,
                     text="Administrar reservas",
                     command=ManageBookingsWindow)
bkgsBtt.grid(row=3, sticky=(W, E), pady=10)
bkgsBtt.grid_forget()
newbkgBtt = ttk.Button(uspw,
                       text="Crear una nueva reserva",
                       command=BookingWindow)
newbkgBtt.grid(row=4, sticky=(W, E), pady=10)
newbkgBtt.grid_forget()

givenUser = ""
givenPassword = ""
cUser = ""
cAdmin = 0

# setup>

root.mainloop()

# importar user/password from csv
# importar reservas from csv
# 1: iniciar sesión (admin/user)
# 2-admin: aceptar o rechazar reservas, administrar reservas
# 2-user: reservar / cancelar (administrar reservas propias)

# un mensaje "* perdiste treinta mil dólares *"

# datos = [reserva[
# id,
# usuario,
# estado de la reserva (0=por aceptar 1=aceptada/en espera, 2=terminada, 3=cancelada/rechazada 4=en realización),
# nombres,
# edades,
# comida (0=sin 1=con "string/comentario"=dieta específica),
# tipo de habitación (0=privado simple, 1=privado doble, 2=compartido simple, 3=compartido doble)
# startDate,
# finishDate (ambos incluyente),
# persona de referencia/contacto,
# comentario]]
# Habitaciones:
# 24 total:
# Baño privado simple: $60 000
# Baño privado doble: $85 000
# 7 total:
# Baño compartido simple: $50 000
# Baño compartido doble: $55 000
