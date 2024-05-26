import sys
import random
import re
import time
from tkinter import *
from tkinter.messagebox import showerror, showinfo
from PIL import ImageTk, Image


def exit_program():
    sys.exit()


colors = {
    1: '#0000FF',  # чисто синий
    2: '#20AF2A',  # глубокий зеленый
    3: '#FF0000',  # ярко-красный
    4: '#B50000',  # темно красный
    5: '#621515',  # коричневый
    6: '#8904EF',  # фиолетовый
    7: '#00FFDE',  # бирюзовый
    8: '#000000'  # черный
}

"""
    Класс кнопки для игры в сапер.

    Атрибуты:
        x (int): Позиция по горизонтали.
        y (int): Позиция по вертикали.
        number (int): Номер кнопки.
        is_mine (bool): Флаг, показывающий, есть ли мина в клетке.
        count_bomb (int): Количество мин вокруг клетки.
        is_open (bool): Флаг, показывающий, была ли кнопка открыта.
        count_flag (int): Количество установленных флажков.
        time_start (float): Время начала игры.
        is_flag (bool): Флаг, показывающий, установлен ли флажок в клетке.
"""


class FieldButton(Button):
    def __init__(self, master, x, y, number, *args, **kwargs):
        super(FieldButton, self).__init__(master, width=3, font=('Courier New bold', 15), *args, **kwargs, bd=3)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False  # есть ли мина
        self.count_bomb = 0  # количество бомб вокруг клетки
        self.is_open = False  # открывали ли кнопку
        self.count_flag = 0  # подсчет флажков или разминирования
        self.time_start = 0  # время начала игры
        self.is_flag = False  # разминировали или нет


"""
    Класс игры в сапер.

    Атрибуты:
        win (Tk): Основное окно игры.
        ROWS (int): Количество строк на поле.
        COLUMNS (int): Количество столбцов на поле.
        MINES (int): Количество мин на поле.
        IS_GAMEOVER (bool): Флаг, показывающий, завершена ли игра.
        IS_FIRST_CLICK (bool): Флаг, показывающий, был ли сделан первый клик.
"""


class MineSweeper:
    win = Tk()
    win.resizable(False, False)
    win.title('Сапер')
    photo = PhotoImage(file='images/MS_icon.png')
    win.iconphoto(False, photo)

    ROWS = 6
    COLUMNS = 6
    MINES = 5
    IS_GAMEOVER = False
    IS_FIRST_CLICK = True

    flag_defuse = ImageTk.PhotoImage(Image.open('images/flag33.png'))
    bomb_color = ImageTk.PhotoImage(Image.open('images/bomb_color.png'))
    bomb_nocolor = ImageTk.PhotoImage(Image.open('images/bomb_nocolor.png'))

    '''__init__(): Инициализация игры.'''

    def __init__(self):
        self.timer = None
        self.index_mines = None
        self.lbl_mines = None
        self.lbl_time = None
        self.flag_position = None
        self.count_flag = None
        self.win_destroy = None
        self.buttons = []
        self.timer_started = False
        self.time_start = 0
        number = 0

        for i in range(self.ROWS + 2):
            temp = []
            for j in range(self.COLUMNS + 2):
                number += 1
                btn = FieldButton(self.win, x=i, y=j, number=number)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind('<Button-3>', self.right_click)
                temp.append(btn)
                # btn.config(bg='#FFFFFF')
            self.buttons.append(temp)

    '''create_widget(): Создание виджетов игры.'''

    def create_widget(self):
        count = 1
        self.flag_position = []
        self.count_flag = self.MINES
        menubar = Menu(self.win)
        self.win.config(menu=menubar)

        settings_menu = Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Старт', command=self.reload)
        settings_menu.add_command(label='Настройки', command=self.create_setting_win)
        settings_menu.add_command(label='Статистика', command=self.create_stat_win)
        settings_menu.add_command(label='Выход', command=exit_program)
        menubar.add_cascade(label='Меню', menu=settings_menu)

        for i in range(1, self.ROWS + 1):
            for j in range(1, self.COLUMNS + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick='wens')
                count += 1

        for i in range(1, self.ROWS + 1):
            self.win.grid_rowconfigure(i, weight=1)

        for i in range(1, self.COLUMNS + 1):
            self.win.grid_columnconfigure(i, weight=1)

        self.lbl_time = Label(text='Начинайте игру!')
        self.lbl_time.grid(row=0, column=1, columnspan=(self.COLUMNS // 2))
        self.lbl_mines = Label(text=f'Флагов осталось: {self.count_flag}')
        self.lbl_mines.grid(row=0, column=((self.COLUMNS // 2) + 1), columnspan=(self.COLUMNS // 2))
        self.update_window_size()

    '''start_timer(): Запуск таймера.'''

    def start_timer(self):
        if not self.timer_started:
            self.time_start = time.time()
            self.timer_started = True
            self.update_time()

    '''update_time(): Обновление отображения времени.'''

    def update_time(self):
        if not self.IS_GAMEOVER and self.timer_started:
            timer = time.time() - self.time_start
            self.lbl_time.config(text=f'Секунд прошло: {int(timer)}')
            self.win.after(1000000, self.update_time)

    '''create_setting_win(): Создание окна настроек.'''

    def create_setting_win(self):
        def change_lvl(mines, row, column):
            row_entry.delete(0, END)
            row_entry.insert(0, row)

            column_entry.delete(0, END)
            column_entry.insert(0, column)

            mines_entry.delete(0, END)
            mines_entry.insert(0, mines)

        win_settings = Toplevel(self.win)
        win_settings.title('Настройки')
        photo = PhotoImage(file='images/settings_icon.png')
        win_settings.iconphoto(False, photo)
        win_settings.geometry('400x280+438+220')
        win_settings.resizable(False, False)  # разрешаем изменять размер окна

        Label(win_settings, text='  Количество строк:').grid(row=0, column=0)
        Label(win_settings, text='       Количество колонок:').grid(row=1, column=0)
        Label(win_settings, text='Количество мин:').grid(row=2, column=0)

        row_entry = Entry(win_settings)
        row_entry.insert(0, str(self.ROWS))
        row_entry.grid(row=0, columnspan=3, column=1, padx=20, pady=20, stick='wens')

        column_entry = Entry(win_settings)
        column_entry.insert(0, str(self.COLUMNS))
        column_entry.grid(row=1, columnspan=3, column=1, padx=20, pady=20, stick='wens')

        mines_entry = Entry(win_settings)
        mines_entry.insert(0, str(self.MINES))
        mines_entry.grid(row=2, columnspan=3, column=1, padx=20, pady=20, stick='wens')

        save_btn = Button(win_settings, text='Применить',
                          command=lambda: self.change_settings(row_entry, column_entry, mines_entry))
        save_btn.grid(row=4, padx=20, pady=20, columnspan=3, stick='wens')

        easy_btn = Button(win_settings, text='Легкий', command=lambda: change_lvl(5, 6, 6))
        easy_btn.grid(row=3, column=0, stick='wens', padx=20)

        normal_btn = Button(win_settings, text='Средний', command=lambda: change_lvl(10, 9, 9))
        normal_btn.grid(row=3, column=1, stick='wens', ipadx=30)

        hard_btn = Button(win_settings, text='Сложный', command=lambda: change_lvl(20, 12, 12))
        hard_btn.grid(row=3, column=2, stick='wens', ipadx=25, padx=20)

        for i in range(5):
            win_settings.grid_rowconfigure(i, weight=1)
        for i in range(2):
            win_settings.grid_columnconfigure(i, weight=1)

    '''reload(): Перезагрузка путем сброса текущего состояния игры'''

    def reload(self):
        [child.destroy() for child in self.win.winfo_children()]  # типа перегруза для удаления применения
        self.__init__()
        self.create_widget()
        self.IS_GAMEOVER = False
        self.IS_FIRST_CLICK = True  # После нажатия - False. Перезагрузка _ возврат флага

    '''change_settings(row, column, mines): Изменение настроек игры.'''

    def change_settings(self, row: Entry, column: Entry, mines: Entry):  # теперь ошибки обрабатываются, все ок
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Ошибка!', 'Вы ввели неверное значение!')
            return

        self.ROWS = int(row.get())
        self.COLUMNS = int(column.get())
        self.MINES = int(mines.get())
        self.reload()
        self.update_window_size()

    '''create_stat_win(): Создание окна статистики.'''

    @staticmethod
    def create_stat_win():
        try:
            with open('logs.txt', 'r') as logs:
                text = logs.read()
                list_game_time = re.findall(r'Время: (\d+)', text)
                list_game_result = re.findall(r'Результат - (\w+)', text)

            total_games = len(list_game_result)
            total_time = sum(int(time) for time in list_game_time)  # Суммируем время игр
            if total_games != 0:
                time_avg = total_time / len(list_game_time)  # Среднее время игры
                win_count = list_game_result.count('Победа')  # Количество побед
                win_avg = (win_count / total_games) * 100  # Процент выигрышей
            else:
                time_avg = 0
                win_avg = 0
            if time_avg == 1:
                showinfo('Статистика', f'Игр сыграно: {total_games}\n'
                                       f'Процент выигрышей: {win_avg:.0f}%\n'
                                       f'Среднее время игры: {time_avg:.0f} секунда')
            elif time_avg == 2 or time_avg == 3 or time_avg == 4:
                showinfo('Статистика', f'Игр сыграно: {total_games}\n'
                                       f'Процент выигрышей: {win_avg:.0f}%\n'
                                       f'Среднее время игры: {time_avg:.0f} секунды')
            else:
                showinfo('Статистика', f'Игр сыграно: {total_games}\n'
                                       f'Процент выигрышей: {win_avg:.0f}%\n'
                                       f'Среднее время игры: {time_avg:.0f} секунд')

        except FileNotFoundError:
            showinfo('Статистика', 'Файл с логами не найден!')

    '''right_click(event): Обработка правого клика мыши.'''

    def right_click(self, event):
        curr_btn = event.widget
        if self.IS_GAMEOVER:
            return  # выходим/завершаем
        if self.IS_FIRST_CLICK:
            return
        list_mines_pos = sorted(self.index_mines)
        if not curr_btn.is_flag and not curr_btn.is_open:
            if self.count_flag == 0:
                return
            curr_btn['command'] = 0
            curr_btn.is_flag = True
            curr_btn['text'] = 'F'
            curr_btn['image'] = self.flag_defuse
            self.count_flag -= 1  # условие проигрыша
            self.flag_position.append(curr_btn.number)
        elif curr_btn.is_flag and not curr_btn.is_open:
            curr_btn.is_flag = False
            curr_btn['text'] = ''
            curr_btn['command'] = lambda button=curr_btn: self.click(button)
            curr_btn['image'] = ''
            self.count_flag += 1
            self.flag_position.remove(curr_btn.number)
        if list_mines_pos == sorted(self.flag_position):
            self.IS_GAMEOVER = True  # Остановить таймер, так как игра выиграна
            showinfo('Победа!', f'Вы выиграли!\n'
                                f'Потрачено секунд: {self.timer:.0f}')
            with open('logs.txt', 'a') as logs:
                logs.write(f'Результат - Победа. Время: {self.timer:.0f} секунд\n')
            self.reload()
        self.lbl_mines.config(text=f'Флагов осталось: {self.count_flag}')

    '''count_mines_buttons(): Подсчет мин вокруг каждой клетки.'''

    def count_mines_buttons(self):  # алгоритм проверки соседей на мины
        for i in range(1, self.ROWS + 1):
            for j in range(1, self.COLUMNS + 1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:  # соседние 8 клеток
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i + row_dx][j + col_dx]
                            if neighbour.is_mine:
                                count_bomb += 1
                btn.count_bomb = count_bomb

    '''count_correct_flags(): Подсчет правильно установленных флажков.'''

    def count_correct_flags(self):
        correct_flags = 0
        for i in range(1, self.ROWS + 1):
            for j in range(1, self.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.is_mine and btn.is_flag:
                    correct_flags += 1
        return correct_flags

    '''click(clicked_button): Обработка левого клика мыши.'''

    def click(self, clicked_button: FieldButton):
        if not self.IS_GAMEOVER:
            if not self.timer_started:
                self.start_timer()
        if self.IS_GAMEOVER:
            return
        if self.IS_FIRST_CLICK:
            self.time_start = time.time()
            self.insert_mines(clicked_button.number)
            self.count_mines_buttons()
            self.tick()
            self.IS_FIRST_CLICK = False

        if clicked_button.is_mine:
            clicked_button.config(text='*', disabledforeground='black')
            clicked_button.is_open = True
            self.IS_GAMEOVER = True
            for i in range(1, self.ROWS + 1):
                for j in range(1, self.COLUMNS + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        if btn.is_flag:
                            btn['image'] = self.bomb_nocolor
                            btn['bg'] = 'green'
                        else:
                            btn['image'] = self.bomb_color
            correct_flags = self.count_correct_flags()
            if correct_flags == 1:
                found_mines_message = f'И найдена {correct_flags} мина'
            elif 2 <= correct_flags <= 4:
                found_mines_message = f'И найдено {correct_flags} мины'
            else:
                found_mines_message = f'И найдено {correct_flags} мин'

            showinfo('Игра закончена!', f'Вы проиграли \n'
                                        f'Потрачено секунд: {self.timer:.0f}\n'
                                        f'{found_mines_message}')

            with open('logs.txt', 'a') as logs:
                logs.write(f'Результат - Проигрыш. Время: {self.timer:.0f} секунд\n')
            self.open_all_buttons()

        else:
            color = colors.get(clicked_button.count_bomb, 'black')
            if clicked_button.count_bomb:
                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
                clicked_button.is_open = True
            else:
                self.find_empty_cells(clicked_button)
        color = colors.get(clicked_button.count_bomb, 'black')
        clicked_button.config(fg=color, relief=SUNKEN)

    '''get_mine_places(exclude_number): Получение местоположения мин.'''

    def get_mine_places(self, exclude_number: int):  # эти два метода отвечают за расположение мин
        indexes = list(range(1, self.COLUMNS * self.ROWS + 1))
        indexes.remove(exclude_number)
        random.shuffle(indexes)
        return indexes[:self.MINES]

    '''find_empty_cells(btn): Поиск пустых клеток.'''

    def find_empty_cells(self, btn: FieldButton):
        queue = [btn]
        while queue:
            curr_btn = queue.pop()
            color = colors.get(curr_btn.count_bomb, 'black')
            if curr_btn.count_bomb:
                curr_btn.config(text=curr_btn.count_bomb, disabledforeground=color)
            else:
                curr_btn.config(text='', disabledforeground=color)
            curr_btn.config(state='disabled', relief=SUNKEN)
            curr_btn.is_open = True
            if curr_btn.count_bomb == 0:
                x, y = curr_btn.x, curr_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        next_btn = self.buttons[x + dx][y + dy]
                        if not next_btn.is_open and not next_btn.is_flag and 1 <= next_btn.x <= self.ROWS and \
                                1 <= next_btn.y <= self.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)

    '''insert_mines(number): Размещение мин на поле.'''

    def insert_mines(self, number: int):  # Чтобы в клавишу мина не попадала
        self.index_mines = self.get_mine_places(number)
        # print(f'Мины в {self.index_mines}')
        for i in range(1, self.ROWS + 1):
            for j in range(1, self.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.number in self.index_mines:
                    btn.is_mine = True

    '''open_all_buttons(): Открытие всех кнопок в конце игры.'''

    def open_all_buttons(self):
        for i in range(1, self.ROWS + 1):
            for j in range(1, self.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    if btn.is_flag:
                        btn.config(bg='green', disabledforeground='black')
                    else:
                        btn.config(bg='red', disabledforeground='black')
                elif btn.count_bomb in colors:
                    color = colors.get(btn.count_bomb, 'black')
                    btn.config(text=btn.count_bomb, fg=color, relief=SUNKEN)

    '''tick(): Обновление таймера.'''

    def tick(self):
        if self.IS_GAMEOVER:
            return
        self.timer = time.time() - self.time_start
        self.lbl_time.config(text=f'Секунд прошло: {self.timer:.0f}')
        self.lbl_time.after(500, self.tick)

    '''update_window_size(): Обновление размеров окон.'''

    def update_window_size(self):
        win_width = self.COLUMNS * 40  # Ширина окна
        win_height = self.ROWS * 40 + 15  # Высота окна
        screen_width = self.win.winfo_screenwidth()
        screen_height = self.win.winfo_screenheight()
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        self.win.geometry(f"{win_width}x{win_height}+{x}+{y}")

    '''start(): Запуск игры.'''

    def start(self):
        self.create_widget()
        win_width = 250  # Ширина окна
        win_height = 275  # Высота окна
        screen_width = self.win.winfo_screenwidth()
        screen_height = self.win.winfo_screenheight()
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        self.win.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.win.mainloop()


if __name__ == "__main__":
    game = MineSweeper()
    game.start()
