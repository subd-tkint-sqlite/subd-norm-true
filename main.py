from tkinter import *
from tkinter import ttk
import backend as back
from sqlite3 import *


with connect('database.db') as db:
    cursor = db.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS table1 (id INTEGER PRIMARY KEY, name TEXT,  expenses TEXT )""")


def list_tables():
    cursor.execute("""SELECT name FROM sqlite_master WHERE type = "table" """)
    return cursor.fetchall()




#  Главное окно
window = Tk()
window.title('subd')
window.minsize(700, 450)


frame_change = Frame(window, width=150, height=150, bg='white')  # блок для функционала субд
frame_view = Frame(window, width=150, height=150, bg='white')  # блок для просмотра базы данных
frame_change.place(relx=0, rely=0, relwidth=1, relheight=1)
frame_view.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)

#переменная хранит Boolean от RadioButton menu
r_var_table = StringVar()
r_var_table.set('table1')

# порядок элементов
heads = []

with connect('database.db') as db:
    cursor = db.cursor()
    cursor.execute('PRAGMA table_info('+str(r_var_table.get())+')')
    column_names = [i[1] for i in cursor.fetchall()]
for row in column_names:
    heads.append(row)

table = ttk.Treeview(frame_view, show='headings', selectmode="browse")  # дерево выполняющее свойство таблицы
table['columns'] = heads  # длина таблицы





lst_tables = []
#переключение между таблицами
def menu_cascade():
    lst_tables2 = []
    for tables in list_tables():
        lst_tables2.append(*tables, )
    print(lst_tables2)
    for word in lst_tables2:
        if word in lst_tables:
            print('if')
            pass
        else:
            lst_tables.append(word)
            filemenu.add_radiobutton(label=word, value=word, variable=r_var_table, command=up_frame)
            print('else')

def information():
    cursor.execute("SELECT * FROM " + str(r_var_table.get()))
    return cursor.fetchall()

# заголовки столбцов и их расположение
for header in heads:
    table.heading(header, text=header, anchor='center')
    table.column(header, anchor='center')


# добавление из бд в таблицу приложения
for row in information():
    table.insert('', END, values=row)
table.pack(expand=YES, fill=BOTH, side=LEFT)


table_name = ttk.Entry(frame_change)
table_name.grid(row=0, column=5, sticky='w', padx=10, pady=10)

def new_table():
    tb = table_name.get()
    with connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS"""+' '+tb+' '+"""(id INTEGER PRIMARY KEY)""")



btn_new_table = ttk.Button(frame_change, text='новая таблица', command=new_table)
btn_new_table.grid(row=5, column=6, columnspan=2, sticky='w', padx=10, pady=10)

# функция обновления таблицы
def refresh():
    with connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(''' SELECT * FROM  ''' + str(r_var_table.get()))
        [table.delete(i) for i in table.get_children()]
        [table.insert('', 'end', values=row) for row in cursor.fetchall()]
        db.commit()

def up_frame():
    all_item_frame = [f for f in frame_view.children]
    for item in all_item_frame:
        frame_view.nametowidget(item).destroy()
    add_frame()


def add_frame():
    heads.clear()
    with connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute('PRAGMA table_info(' + str(r_var_table.get()) + ')')
        column_names = [i[1] for i in cursor.fetchall()]
    for row in column_names:
        heads.append(row)
    table = ttk.Treeview(frame_view, show='headings', selectmode="browse")  # дерево выполняющее свойство таблицы
    table['columns'] = heads
    for header in heads:
        table.column(header, anchor='center')
        table.heading(header, text=header, anchor='center')
    for row in information():
        table.insert('', END, values=row)
    table.pack(expand=YES, fill=BOTH, side=LEFT)

    scrollpanel = ttk.Scrollbar(frame_view, command=table.yview)
    table.configure(yscrollcommand=scrollpanel.set)
    scrollpanel.pack(side=RIGHT, fill=Y)
    table.pack(expand=YES, fill=BOTH)


# функция обработчика событий по нажатию лкм
def on_select(event):
    global id_sel
    global set_col
    id_sel = table.item(table.focus())
    id_sel = id_sel.get('values')[0]
    col = table.identify_column(event.x)
    set_col = table.column(col)
    set_col = set_col.get('id')
table.bind('<ButtonRelease-1>', on_select)



def add_table():
    newcol = f_column.get()
    heads.append(newcol)
    with connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("""ALTER TABLE """ + ' ' + str(r_var_table.get()) + ' ' + """ ADD COLUMN '%s' 'TEXT' """ % newcol)
        db.commit()
        up_frame()



def del_table():
    with connect('database.db') as db:
        cursor = db.cursor()

        cursor.execute("""ALTER TABLE """ + ' ' + str(r_var_table.get()) + ' ' + """ DROP COLUMN """ + set_col)
        db.commit()
        up_frame()




# функция добавления новых записей
def form_submit():
    name = f_name.get()
    expenses = f_expenses.get()
    insert_inf = (name, expenses)
    with connect('database.db') as db:
        cursor = db.cursor()
        query = """ INSERT INTO """ + ' '+ str(r_var_table.get()) + """(name, expenses) VALUES (?, ?)"""
        cursor.execute(query, insert_inf)
        db.commit()
        up_frame()


# функция удалить
def delete():
    with connect('database.db') as db:
        cursor = db.cursor()
        id = id_sel
        cursor.execute('''DELETE FROM  ''' + ' ' + str(r_var_table.get()) + ''' WHERE id = ?''', (id,))
        db.commit()
        up_frame()


# функция изменения дб
def changeDB():
    with connect('database.db') as db:
        cursor = db.cursor()
        id = id_sel
        whatchange = f_change.get()
        if set_col != 'id':
            cursor.execute("""Update """ + " " + str(r_var_table.get()) + """ set """ + ' ' + set_col + """ = ? where id = ? """,
                                               (whatchange, id))
            db.commit()
            refresh()







# контекстное меню
mainmenu = Menu(window)
window.config(menu=mainmenu)



filemenu = Menu(mainmenu, tearoff=0, postcommand=menu_cascade)
mainmenu.add_cascade(label="Таблицы",
                     menu=filemenu)

# добавления новых имен в бд
l_name = ttk.Label(frame_change, text="Имя")
f_name = ttk.Entry(frame_change)
l_name.grid(row=0, column=0, sticky='w', padx=10, pady=10)
f_name.grid(row=0, column=1, sticky='w', padx=10, pady=10)


# добавления новых платежей в бд
l_expenses = ttk.Label(frame_change, text="Платеж")
f_expenses = ttk.Entry(frame_change)
l_expenses.grid(row=1, column=0, sticky='w', padx=10, pady=10)
f_expenses.grid(row=1, column=1, sticky='w', padx=10, pady=10)


#  изменения бд
l_change = ttk.Label(frame_change, text="Заменить на:")
f_change = ttk.Entry(frame_change)  # entry на что меняем прошлое имя в бд
l_change.grid(row=3, column=0, sticky='w', padx=10, pady=10)
f_change.grid(row=3, column=1, sticky='w', padx=10, pady=10)


f_column = ttk.Entry(frame_change)
f_column.grid(row=4, column=4, sticky='w', padx=10, pady=10)


#  кнопка добавить
btn_submit = ttk.Button(frame_change, text="Добавить", command=form_submit)
btn_submit.grid(row=0, column=3, columnspan=2, sticky='w', padx=10, pady=10)

#  кнопка удалить
btn_delete = ttk.Button(frame_change, text="Удалить", command=delete)
btn_delete.grid(row=1, column=3, columnspan=2, sticky='w', padx=10, pady=10)

#  кнопка изменить
but_change = ttk.Button(frame_change, text='Изменить', command=changeDB)
but_change.grid(row=3, column=3, columnspan=2, sticky='w', padx=10, pady=10)

#  кнопка вызывающая справку
btn_reference = ttk.Button(frame_change, text="Справка", command=back.show_info)
btn_reference.grid(row=4, column=0, sticky='w', padx=10, pady=10)


btn_add_column = ttk.Button(frame_change, text='новая', command=add_table)
btn_add_column.grid(row=5, column=4, columnspan=2, sticky='w', padx=10, pady=10)

btn_del_column = ttk.Button(frame_change, text='удалить', command=del_table)
btn_del_column.grid(row=5, column=5, columnspan=2, sticky='w', padx=10, pady=10)

#  скроллбар
scrollpanel = ttk.Scrollbar(frame_view, command=table.yview)
table.configure(yscrollcommand=scrollpanel.set)
scrollpanel.pack(side=RIGHT, fill=Y)
table.pack(expand=YES, fill=BOTH)

window.update()
table.update()

window.mainloop()
