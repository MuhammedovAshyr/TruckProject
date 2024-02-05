from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tkinter.simpledialog import Dialog
import datetime
import random


class CardInfoDialog(Dialog):
    def __init__(self, parent, headers, card_info):
        self.headers = headers
        self.card_info = card_info
        Dialog.__init__(self, parent)

    def body(self, master):
        Label(master, text="Информация о карточке").grid(row=0, column=0, columnspan=2)
        for i, (header, value) in enumerate(zip(self.headers, self.card_info)):
            Label(master, text=header).grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")
            Label(master, text=str(value)).grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")
        return None


class AddCardWindow:
    def __init__(self, parent, headers, data_list, update_treeview, update_canvas):
        self.window = Toplevel(parent)
        self.window.title("Добавить карточку")

        self.headers = headers
        self.data_list = data_list
        self.update_treeview = update_treeview
        self.update_canvas = update_canvas

        self.entry_vars = []

        for header in headers:
            label = Label(self.window, text=header)
            label.grid(row=headers.index(header), column=0, padx=5, pady=5, sticky="e")

            entry_var = StringVar()
            entry = Entry(self.window, textvariable=entry_var, state='readonly' if header in ["Номер чека", "Номер клиента"] else 'normal')
            entry.grid(row=headers.index(header), column=1, padx=5, pady=5, sticky="w")

            self.entry_vars.append(entry_var)

        # Generate and set a random card number
        random_card_number = random.randint(1000, 9999)
        self.entry_vars[headers.index("Номер чека")].set(str(random_card_number))

        random_card_number = random.randint(10000, 99999)
        self.entry_vars[headers.index("Номер клиента")].set(str(random_card_number))

        # Button to add the card
        button_add_card = Button(self.window, text="Добавить", command=self.add_card)
        button_add_card.grid(row=len(headers) + 1, columnspan=2, pady=10)

    def add_card(self):
        new_card_data = [entry_var.get() for entry_var in self.entry_vars]
        self.window.destroy()
        self.data_list.insert(0, tuple(new_card_data))  # Insert at the beginning of the list
        self.update_treeview()
        self.update_canvas()


class TripListWindow:
    def __init__(self, parent, card_objects, truck_objects):
        self.window = Toplevel(parent)
        self.window.title("Список рейсов")

        self.card_objects = card_objects
        self.truck_objects = truck_objects

        # Creating the Treeview
        self.tree_trips = ttk.Treeview(self.window, columns=("Карточка", "Грузовик"), show="headings")
        self.tree_trips.heading("Карточка", text="Карточка")
        self.tree_trips.heading("Грузовик", text="Грузовик")

        self.tree_trips.column("Карточка", width=200)
        self.tree_trips.column("Грузовик", width=200)

        self.tree_trips.pack(pady=10, padx=10)

        # Populate the Treeview with data
        self.populate_treeview()

    def populate_treeview(self):
        for card_data in self.card_objects:
            card_number = card_data['number']
            truck_number = card_data['in_truck'] if card_data['in_truck'] else "Не добавлена в грузовик"
            self.tree_trips.insert("", "end", values=(card_number, truck_number))


class DragNDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Drag n drop')
        self.root.geometry("1100x850")

        w = 800
        h = 500

        self.my_canvas = Canvas(root, width=w, height=h, bg="white")
        self.my_canvas.pack(pady=20)

        self.truck_original_img = Image.open("C:\\PycharmProjects\\truck.png")
        truck_resized_img = self.truck_original_img.resize((100, 100))
        self.truck_img = ImageTk.PhotoImage(truck_resized_img)

        # Готовые данные из запроса
        self.data_list = [
            (datetime.datetime(2023, 1, 1, 16, 42), 6286, 10, 65415, 'Иван', 993123451),
            (datetime.datetime(2023, 1, 2, 13, 10), 1239, 151, 14142, 'Владимир', 993432151),
            (datetime.datetime(2023, 3, 17, 14, 1), 4709, 30, 55363, 'Ирина', 993045986),
            (datetime.datetime(2023, 7, 31, 20, 30), 4321, 50, 11122, 'Николай', 993906360),
            (datetime.datetime(2024, 6, 27, 10, 7), 5975, 40, 74514, 'Ксения', 993125048)
        ]

        # Создание списка карточек и грузовиков
        self.card_objects = []
        self.truck_objects = []

        # Создание функций для работы с перетаскиванием
        def move_card(event, data):
            dx = event.x - data['start_x']
            dy = event.y - data['start_y']

            self.my_canvas.move(data['id'], dx, dy)
            self.my_canvas.move(data['rect_id'], dx, dy)

            data['start_x'] = event.x
            data['start_y'] = event.y

            self.check_overlap(data)

        def on_button_press_card(event, data):
            data['start_x'] = event.x
            data['start_y'] = event.y

        def on_button_release_card(event, data):
            if data['in_truck']:
                self.my_canvas.itemconfig(data['id'], state="hidden")
                self.my_canvas.itemconfig(data['rect_id'], state="hidden")
                self.show_success_message(data, data['in_truck'])
                data['in_truck'] = None

        def check_overlap(data):
            bbox1 = self.my_canvas.bbox(data['id'])
            for truck_data in self.truck_objects:
                bbox2 = self.my_canvas.bbox(truck_data['id'])
                if bbox1[0] < bbox2[2] and bbox1[2] > bbox2[0] and bbox1[1] < bbox2[3] and bbox1[3] > bbox2[1]:
                    data['in_truck'] = truck_data['number']
                    self.my_canvas.itemconfig(data['rect_id'], outline="green")
                    return
            data['in_truck'] = None
            self.my_canvas.itemconfig(data['rect_id'], outline="black")

        def show_success_message(data, truck_number):
            message = f"Карточка {data['number']} успешно добавлена в грузовик №{truck_number}"
            messagebox.showinfo("Успех", message)
            self.show_card_info(truck_number)

        def search_by_card_number():
            card_number = entry_search.get().strip()  # Get the entered card number as a string

            # Clear existing items in the Treeview
            for item in self.tree_invoices.get_children():
                self.tree_invoices.delete(item)

            # Filter and insert matching items based on the entered card number
            for i, invoice in enumerate(self.data_list):
                if str(invoice[1]) == card_number:
                    self.tree_invoices.insert("", "end", values=(
                        invoice[0], invoice[1], invoice[2], invoice[3], invoice[4], invoice[5]))

            # Adjust the height of the Treeview based on the number of rows
            self.tree_invoices.grid_configure()

        # Создание карточек на холсте
        for i, data in enumerate(self.data_list):
            text_data = "\n".join(map(str, data))
            card_id = self.my_canvas.create_text(50, 25 + i * 100, text=text_data, anchor="nw")

            # Создание рамки вокруг карточки
            bbox = self.my_canvas.bbox(card_id)
            rect_id = self.my_canvas.create_rectangle(bbox, outline="black", width=2)

            self.card_objects.append(
                {'id': card_id, 'number': data[1], 'rect_id': rect_id, 'start_x': 0, 'start_y': 0, 'in_truck': None, 'card_info': data})

            self.my_canvas.tag_bind(card_id, '<B1-Motion>', lambda event, data=self.card_objects[i]: move_card(event, data))
            self.my_canvas.tag_bind(card_id, '<ButtonPress-1>',
                                   lambda event, data=self.card_objects[i]: on_button_press_card(event, data))
            self.my_canvas.tag_bind(card_id, '<ButtonRelease-1>',
                                   lambda event, data=self.card_objects[i]: on_button_release_card(event, data))

        # Создание грузовиков на холсте
        for i in range(3):
            truck_id = self.my_canvas.create_image(650, 100 + i * 150, image=self.truck_img)
            ab_part = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2))
            truck_number = f"{ab_part} {random.randint(1000, 9999)} AG"  # Generate a random truck number
            truck_label = Label(self.root, text=truck_number)
            truck_label.place(x=760, y=150 + i * 150)

            self.truck_objects.append({'id': truck_id, 'number': i + 1, 'label': truck_label})

            # Привязка события щелчка мыши на грузовике
            self.my_canvas.tag_bind(truck_id, '<Button-1>',
                                    lambda event, truck_number=i + 1: self.show_card_info(truck_number))

        # Фрейм для отображения списка накладных
        self.frame_invoices = ttk.Frame(self.root)
        self.frame_invoices.pack(side=BOTTOM, padx=10, pady=10, fill=Y)

        # Список накладных
        self.tree_invoices = ttk.Treeview(self.frame_invoices, columns=(
            "Дата", "Номер чека", "Масса груза", "Номер клиента", "Имя клиента", "Телефон клиента"), show="headings")
        self.tree_invoices.heading("Дата", text="Дата и время")
        self.tree_invoices.heading("Номер чека", text="Номер чека")
        self.tree_invoices.heading("Масса груза", text="Масса груза")
        self.tree_invoices.heading("Номер клиента", text="Номер клиента")
        self.tree_invoices.heading("Имя клиента", text="Имя клиента")
        self.tree_invoices.heading("Телефон клиента", text="Телефон клиента")

        # Set column widths using grid method
        self.tree_invoices.column("Дата", width=150)
        self.tree_invoices.column("Номер чека", width=100)
        self.tree_invoices.column("Масса груза", width=100)
        self.tree_invoices.column("Номер клиента", width=100)
        self.tree_invoices.column("Имя клиента", width=100)
        self.tree_invoices.column("Телефон клиента", width=150)

        self.tree_invoices.grid(row=0, column=0, sticky="nsew")

        # Entry and button for searching by card number
        entry_search = Entry(self.frame_invoices)
        button_search = ttk.Button(self.frame_invoices, text="Поиск", command=search_by_card_number)

        entry_search.grid(row=1, column=0, padx=5, pady=5)
        button_search.grid(row=2, column=0, padx=5, pady=5)

        # Button to open the window for adding a new card
        button_add_card = ttk.Button(self.frame_invoices, text="Добавить карточку", command=self.open_add_card_window)
        button_add_card.grid(row=3, column=0, padx=5, pady=5)

        # Button to open the TripListWindow
        button_trip_list = ttk.Button(self.frame_invoices, text="Список рейсов", command=self.open_trip_list_window)
        button_trip_list.grid(row=4, column=0, padx=5, pady=5)

        # Button to update the list of invoices
        self.create_update_button()

        # Обновление списка накладных
        self.update_treeview()

    def create_update_button(self):
        # Button to update the list of invoices
        button_update = ttk.Button(self.frame_invoices, text="Обновить", command=self.update_treeview)
        button_update.grid(row=0, column=1, padx=5, pady=5)

    def open_add_card_window(self):
        headers = ["Дата и время", "Номер чека", "Масса груза", "Номер клиента", "Имя клиента", "Телефон клиента"]
        AddCardWindow(self.root, headers, self.data_list, self.update_treeview, self.update_canvas)

    def open_trip_list_window(self):
        TripListWindow(self.root, self.card_objects, self.truck_objects)

    def update_treeview(self):
        # Clear existing items in the Treeview
        for item in self.tree_invoices.get_children():
            self.tree_invoices.delete(item)

        num_rows = len(self.data_list)
        tree_height = min(5, num_rows)  # Set the height to a maximum of 5 or the number of rows, whichever is smaller
        self.tree_invoices["height"] = tree_height

        for i, invoice in enumerate(self.data_list):
            self.tree_invoices.insert("", "end", values=(
                invoice[0], invoice[1], invoice[2], invoice[3], invoice[4], invoice[5]))

        # Adjust the height of the Treeview based on the number of rows
        self.tree_invoices.grid_configure()

    def update_canvas(self):
        # Создание карточки на холсте для последней добавленной записи
        latest_data = self.data_list[0]  # Get the first element since we inserted at the beginning
        text_data = "\n".join(map(str, latest_data))
        card_id = self.my_canvas.create_text(175, 25, text=text_data, anchor="nw")

        # Создание рамки вокруг карточки
        bbox = self.my_canvas.bbox(card_id)
        rect_id = self.my_canvas.create_rectangle(bbox, outline="black", width=2)

        self.card_objects.insert(
            0, {'id': card_id, 'number': latest_data[1], 'rect_id': rect_id, 'start_x': 0, 'start_y': 0, 'in_truck': None, 'card_info': latest_data})

        self.my_canvas.tag_bind(card_id, '<B1-Motion>', lambda event, data=self.card_objects[0]: self.move_card(event, data))
        self.my_canvas.tag_bind(card_id, '<ButtonPress-1>',
                               lambda event, data=self.card_objects[0]: self.on_button_press_card(event, data))
        self.my_canvas.tag_bind(card_id, '<ButtonRelease-1>',
                               lambda event, data=self.card_objects[0]: self.on_button_release_card(event, data))

    def move_card(self, event, data):
        dx = event.x - data['start_x']
        dy = event.y - data['start_y']

        self.my_canvas.move(data['id'], dx, dy)
        self.my_canvas.move(data['rect_id'], dx, dy)

        data['start_x'] = event.x
        data['start_y'] = event.y

        self.check_overlap(data)

    def on_button_press_card(self, event, data):
        data['start_x'] = event.x
        data['start_y'] = event.y

    def on_button_release_card(self, event, data):
        if data['in_truck']:
            self.my_canvas.itemconfig(data['id'], state="hidden")
            self.my_canvas.itemconfig(data['rect_id'], state="hidden")
            self.show_success_message(data, data['in_truck'])
            data['in_truck'] = None

    def check_overlap(self, data):
        bbox1 = self.my_canvas.bbox(data['id'])
        for truck_data in self.truck_objects:
            bbox2 = self.my_canvas.bbox(truck_data['id'])
            if bbox1[0] < bbox2[2] and bbox1[2] > bbox2[0] and bbox1[1] < bbox2[3] and bbox1[3] > bbox2[1]:
                data['in_truck'] = truck_data['number']
                self.my_canvas.itemconfig(data['rect_id'], outline="green")
                return
        data['in_truck'] = None
        self.my_canvas.itemconfig(data['rect_id'], outline="black")

    def show_success_message(self, data, truck_number):
        message = f"Карточка {data['number']} успешно добавлена в грузовик №{truck_number}"
        messagebox.showinfo("Успех", message)
        self.show_card_info(truck_number)

    def show_card_info(self, truck_number):
        for card_data in self.card_objects:
            if card_data['in_truck'] == truck_number:
                card_info = card_data['card_info']
                headers = ["Дата и время", "Номер чека", "Масса груза", "Номер клиента", "Имя клиента", "Телефон клиента"]
                CardInfoDialog(self.root, headers, card_info)


if __name__ == "__main__":
    root = Tk()
    app = DragNDropApp(root)
    root.mainloop()
