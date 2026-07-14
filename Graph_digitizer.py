import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def image_error():
    tk.messagebox.showwarning(title="Предупреждение", message="Необходимо загрузить изображение!")

def calibration_error():
    tk.messagebox.showwarning(title="Предупреждение", message="Перед добавлением точек откалибруйте оси!")

def points_absent_error():
    tk.messagebox.showwarning(title="Предупреждение", message="Точки отсутствуют!")

def points_save_error():
    tk.messagebox.showwarning(title="Предупреждение", message="Для сохранения графика необходимо указать минимум 2 точки!\nДобавьте точки!")

def saved_graphs_error(button):
    tk.messagebox.showwarning(title="Предупреждение", message="Не удается записать файл!\nОтсутствуют сохраненные графики!")


class Graph_digitalizer():
    def __init__(self):
        self.file_path = None                           # Путь до графика
        self.image_flag = False                         # Флаг, что график загружен
        self.calibration_flag = False                   # Флаг, что график откалиброван
        self.file_record_flag = False                   # Флаг, что файл был записан

        self.finish_list = []                           # Список, который будет хранить все графики
        self.names_list = []
        self.points = []
        self.graph_start_coordinats = None
        self.graph_x_max = None
        self.graph_y_max = None

        self.root = tk.Tk()                             # создаем корневой объект - окно
        self.root.title("Оцифровщик графиков")          # устанавливаем заголовок окна
        self.root.iconbitmap(default="data/Logo.ico")
        self.root.geometry("1200x800")                  # устанавливаем размеры окна

        self.setup()


    def setup(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill='x', padx=0, pady=5)       # Настройка размера рамки кнопок

        open_file = tk.Button(btn_frame, text="Открыть изображение", command=self.open_file_func).pack(side='left')
        calibration = tk.Button(btn_frame, text="Калибровка осей", command=self.calibration_func).pack(side='left')
        add_points = tk.Button(btn_frame, text="Добавить точки", command=self.add_points_func).pack(side='left')
        clear_points = tk.Button(btn_frame, text="Очистить точки", command=self.clear_points_func).pack(side='left')
        save_graph = tk.Button(btn_frame, text="Сохранить график", command=self.save_graph_func).pack(side='left')
        # delete_graphs = tk.Button(btn_frame, text="Удалить графики",).pack(side='left')
        export = tk.Button(btn_frame, text="Экспортировать в файл", command=self.export_func).pack(side='left')
        exit = tk.Button(btn_frame, text="Выход", command=self.exit).pack(side='right')

        self.status_text = tk.Label(
            self.root, 
            text="Для начала работы откройте изображение графика", 
            font=("Arial", 16),
            foreground="black"
        )
        self.status_text.pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(16,12))
        # plt.title("Для начала работы откройте изображение графика\n\n")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)               # Convert the Figure to a tkinter widget
        self.canvas.get_tk_widget().pack()                                   # Show the widget on the screen
        self.canvas.draw()                                                   # Draw the graph on the canvas?


    def open_file_func(self):
        file_types = [("Images", "*.png *.jpg *.jpeg")]
        self.file_path = filedialog.askopenfilename(filetypes=file_types)

        if (self.file_path != ""):
            self.image_flag = True
            self.calibration_flag = False
            self.img = plt.imread(self.file_path)
            self.ax.clear()
            self.ax.imshow(self.img)                        # Показать график
            # self.ax.set_title("Изображение загружено. Нажмите 'Калибровка осей'\n\n")
            self.canvas.draw()
            
            status = "Изображение загружено. Нажмите 'Калибровка осей'"
            self.set_status(status)
            self.initialization_points()                ##
            self.file_record_flag = False                  


    def calibration_func(self):
        # self.calibration_flag = False
        if (self.image_flag == False):
            image_error()
        
        else:
            messagebox.showinfo("Калибровка", 
                "Сейчас необходимо кликнуть 3 точки на графике:\n\n"
                "1. Точка начала координат\n"
                "2. Точка максимума X\n"
                "3. Точка максимума Y")    
            
            status = "Установите точку начала координат"
            self.set_status(status)
            self.graph_start_coordinats = plt.ginput(n=1, timeout=0, show_clicks=True)[0]
            # print(self.graph_start_coordinats)

            status = "Установите точку максимума оси X"
            self.set_status(status)
            self.graph_x_max = plt.ginput(n=1, timeout=0, show_clicks=True)[0]

            status = "Установите точку максимума оси Y"
            self.set_status(status)
            self.graph_y_max = plt.ginput(n=1, timeout=0, show_clicks=True)[0]

            status = "Введите значение"
            self.set_status(status)

            self.real_x_min = simpledialog.askfloat("Калибровка", "Значение X в начале координат:", initialvalue=0, parent=self.root)
            self.real_x_max = simpledialog.askfloat("Калибровка", "Максимальное значение X:", initialvalue=0, parent=self.root)
            self.real_y_min = simpledialog.askfloat("Калибровка", "Значение Y в начале координат:", initialvalue=0, parent=self.root)
            self.real_y_max = simpledialog.askfloat("Калибровка", "Максимальное значение Y:", initialvalue=0, parent=self.root)

            status = "Калибровка завершена. Теперь вы можете добавить точки"
            self.set_status(status)
            self.calibration_flag = True


    def conversation_coordinates(self, point):                          # Пока что будет работать только для графиков, где оси XY расположены геометрически верно
        graph_min_x = self.graph_start_coordinats[0]
        graph_min_y = self.graph_start_coordinats[1]
        graph_max_x = self.graph_x_max[0]
        graph_max_y = self.graph_y_max[1]

        graph_len_x = graph_max_x - graph_min_x
        graph_len_y = graph_max_y - graph_min_y

        real_len_x = self.real_x_max - self.real_x_min
        real_len_y = self.real_y_max - self.real_y_min

        x_val = point[0]
        y_val = point[1]

        x = (x_val - graph_min_x) * real_len_x / graph_len_x
        y = (y_val - graph_min_y) * real_len_y / graph_len_y
        return (x, y)


    def add_points_func(self):
        if (self.image_flag == False):
            image_error()

        elif (self.calibration_flag == False):
            calibration_error()

        else:
            if (self.file_record_flag == True):
                self.file_record_flag = False                   # Сразу же обнуляю флаг
                length = len(self.names_list)
                result = messagebox.askyesno("Подтверждение",
                     f"Некоторые графики были записаны в файл ранее ({length} граф.)\nЖелаете удалить их?",
                     parent=self.root)
                
                if (result == True):
                    self.finish_list.clear()
                    self.names_list.clear()

            self.points.clear()
            # messagebox.showinfo("Добавление точек", 
            #     "Кликайте по точкам графика.\nНажмите Enter для завершения.
            # \n"\      Можно дописать про ПКМ
                    # "Помните, что чем больше точек, тем выше точность графика")

            status = "Кликайте по точкам графика. Для завершения нажмите Enter."
            self.set_status(status)

            lst = plt.ginput(n=-1, timeout=0, show_clicks=True)
            # print(lst)          ###
            for i in lst:
                coordinates = self.conversation_coordinates(i)
                self.points.append(coordinates)
                # print(i)
            # print(self.points)      ###
            status = f"Точек установлено: {len(self.points)}. Теперь вы можете сохранить график"
            self.set_status(status)

            # self.debugging_print()                # Отладочный принт


    def debugging_print(self):
        x = []
        y = []
        for i in self.points:
            x.append(i[0])
            y.append(i[1])

        plt.figure()
        plt.plot(x, y, marker='o')
        plt.grid(True)
        plt.show()


    def clear_points_func(self):
        if (self.image_flag == False):
            image_error()
        
        elif (len(self.points) == 0):
            points_absent_error()

        else:
            self.points.clear()
            status = f"Точек установлено: {len(self.points)}"
            self.set_status(status)


    def save_graph_func(self):
        if (self.image_flag == False):
            image_error()

        elif (len(self.points) < 2):
            points_save_error()

        else:
            graph_name = simpledialog.askstring("Сохранение", "Вы можете задать имя графика.\n\n"
                                                "Чтобы пропустить нажмите OK.", parent=self.root)

            if (graph_name is not None):

                if (graph_name == ""):
                    self.names_list.append("No_name")

                else:
                    self.names_list.append(graph_name)

                self.finish_list.append(self.points.copy())
                self.points.clear()
                status = "График сохранен"
                self.set_status(status)


    def export_func(self):
        if (self.image_flag == False):
            image_error()

        elif (len(self.finish_list) == 0):
            saved_graphs_error()

        else:
            lenght = len(self.names_list)
            file_name = simpledialog.askstring("Сохранение", "Введите имя файла без расширения!", parent=self.root)

            if (file_name is not None) and (file_name != ""):
                file_name += ".csv"
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write("X,Y")
                    for i in range(lenght):
                        file.write(f"\nFile name: {self.names_list[i]}")
                        lst = self.finish_list[i]
                        for elem in lst:
                            file.write(f"\n{elem[0]},{elem[1]}")
                    status = f"Файл '{file_name}' сохранен"
                    self.set_status(status)
                    self.file_record_flag = True


    def initialization_points(self):                        # Инициализация значений координат нового файла(графика)
        self.finish_list.clear()
        self.names_list.clear()
        self.points.clear()
        self.graph_start_coordinats = None
        self.graph_x_max = None
        self.graph_y_max = None


    def set_status(self, text, color="black"):
        self.status_text.config(text=text, foreground=color)


    def start(self):
        self.root.mainloop()


    def exit(self):
        sys.exit(0)


if __name__ == "__main__":
    program = Graph_digitalizer()
    program.start()