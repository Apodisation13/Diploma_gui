from tkinter import *
from tkinter import messagebox, TclError
from PIL import Image, ImageTk, UnidentifiedImageError
from classes_try import VkPhotos, YandexUploader
import requests
from io import BytesIO
from time import sleep


class ProfileWall:
    def __init__(self, vk_album_list, vk_album_name, vk_num_of_photos, y, on_page):
        self.vk_album_list = vk_album_list  # список со словарями и ссылками
        self.vk_album_name = vk_album_name  # название альбома
        self.vk_num_of_photos = vk_num_of_photos  # количество фото там

        self.on_page = on_page  # на одной странице сколько фоток
        self.page_num = 1  # номер страницы
        self.counter = 0  # счётчик диапазона показываемых фото - 0,10,20,30

        self.x = 10
        self.y = y

        self.first_enter = True  # для первого входа

        self.group_links = []  # список кнопок с картинками, чтобы потом удалять его при нажатии >> и <<
        self.group_elements = []  # список с кнопками вперёд, назад и лейблом, чтобы удалить его по загрузке всех

        font = ("Comic Sans MS", 12)
        self.show_b = Button(text="Показать", bg="green", font=font, command=self.show)

    def show(self):
        def send(m):
            w = m.widget
            print(w._name)
            yandex_uploader = YandexUploader()
            yandex_uploader.upload_one(vk.user_id,
                                       self.vk_album_list[int(w._name[7:]) - b_first + self.counter],
                                       self.vk_album_name)
            messagebox.showinfo("Загрузка", yandex_uploader.status)

        def hide():
            for each in self.group_links:
                each.destroy()
            self.show_b.config(text="Показать", command=self.show)

        def next_page():
            if self.vk_num_of_photos <= self.counter + self.on_page:
                messagebox.showwarning("Ошибка", "Дальше фото нет")
            else:
                self.counter += self.on_page
                self.page_num += 1
                for each in self.group_links:
                    each.destroy()
                page_lbl.config(text=f"Стр{self.page_num}")
                self.show()

        def prev_page():
            if self.counter == 0:
                page_lbl.config(text="Стр1")
                messagebox.showwarning("Ошибка", "Дальше альбомов нет")
            else:
                self.counter -= self.on_page
                self.page_num -= 1
                page_lbl.config(text=f"Стр{self.page_num}")
                for each in self.group_links:
                    each.destroy()
                self.show()

        self.show_b.config(text="Скрыть", command=hide)

        xx = self.x + 290
        yy = self.y - 10

        if self.vk_num_of_photos - self.counter < self.on_page:
            max_on_page = self.vk_num_of_photos - self.counter
        else:
            max_on_page = self.on_page
        print(self.counter, max_on_page)

        for i in range(self.counter, max_on_page + self.counter):
            for key, value in self.vk_album_list[i].items():
                # PIL.UnidentifiedImageError
                try:
                    response = requests.get(value)
                    button_image = Image.open(BytesIO(response.content))
                    button_image = button_image.resize((100, 100), Image.ANTIALIAS)
                    button_image = ImageTk.PhotoImage(button_image)
                except UnidentifiedImageError:
                    button_image = None
                root.update()
                sleep(0.33)
                name = Button(image=button_image, text=i)
                name.image = button_image
                name.bind("<Button-1>", send)
                name.place(x=xx, y=yy, width=100, height=100)
                self.group_links.append(name)
                b_last = int(name._name[7:])
                # тут имя кнопки выглядит типа 'ButtonX - кавычка+6 символов = 7 - и дальше сам номер
                b_first = b_last - max_on_page + 1
                xx += 110
        print(b_first, b_last)

        if self.vk_num_of_photos > 10 and self.first_enter:
            prev_button = Button(text="<<<", bg="grey", font=("Courier", 8), command=prev_page)
            prev_button.place(x=1170, y=self.y + 95, width=50, height=20)
            page_lbl = Label(text=f"Стр{self.page_num}", bg="grey", font=("Courier", 8))
            page_lbl.place(x=1250, y=self.y + 95, width=50, height=20)
            next_button = Button(text=">>>", bg="grey", font=("Courier", 8), command=next_page)
            next_button.place(x=1330, y=self.y + 95, width=50, height=20)
            self.group_elements += [prev_button, page_lbl, next_button]
            self.first_enter = False

    def upload_all(self):
        yandex_uploader = YandexUploader()
        yandex_uploader.upload_all(vk.user_id, self.vk_album_list, self.vk_album_name)
        messagebox.showinfo("Загрузка", yandex_uploader.status)
        for each in self.group_elements:
            each.destroy()
        for each in self.group_links:
            each.destroy()
        # НАДО ОБНУЛИТЬСЯ ЧТОБЫ
        # self.profile()  # ПОКА НЕ ПОНИМАЮ ЗАЧЕМ ЭТО

    def main_info(self):

        x = self.x
        y = self.y

        if self.vk_num_of_photos != 0:
            font = ("Comic Sans MS", 12)
            album_l = Label(text=self.vk_album_name, bg="grey", font=font)
            album_l.place(x=x, y=y, width=100, height=50)
            album_count_l = Label(text=f'Фоток: {self.vk_num_of_photos}', font=font)
            album_count_l.place(x=x, y=y + 60, width=100, height=20)

            self.show_b.place(x=x + 100 + 30, y=y, width=90, height=25)
            upload_all_b = Button(text="Загрузить все", bg="OrangeRed2", font=font, command=self.upload_all)
            upload_all_b.place(x=x + 100 + 30, y=y + 25, width=150, height=25)
            self.group_elements += [album_l, album_count_l, self.show_b, upload_all_b]


class Album:
    def __init__(self, album_name, num_of_photos, y, on_page):

        self.album_list = []  # список со словарями и ссылками

        self.album_name = album_name  # название альбома
        self.num_of_photos = num_of_photos  # количество фото там

        self.on_page = on_page  # на одной странице сколько фоток
        self.page_num = 1  # номер страницы фотографий в альбоме
        self.counter = 0  # счётчик диапазона показываемых фото - 0,10,20,30

        self.x = 10
        self.y = y

        self.first_enter = True  # для первого входа

        self.group_links = []  # список кнопок с картинками, чтобы потом удалять его при нажатии >> и <<
        self.group_elements = []  # список с кнопками вперёд, назад и лейблом, чтобы удалить его по загрузке всех

        font = ("Comic Sans MS", 12)
        self.show_b = None

        self.a_num = 0  # для того чтобы собрать ссылки для нового альбома
        self.group_a = []  # по сути в ней сейчас только denied_lbl, но раньше было что-то ещё...
        self.page_num_a = 1  # номер страницы альбома

        self.f_a = True

        self.page_lbl = Label(text=f"Альбом{self.page_num_a}", bg="grey", font=font)
        self.main_info()

    def next_album(self):

        self.f_a = True

        if vk.album_count <= self.a_num + 1:
            messagebox.showwarning("Ошибка", "Дальше альбомов нет")
        else:
            for each in self.group_a:
                each.destroy()
            for each in self.group_links:
                each.destroy()
            self.a_num += 1
            self.page_num_a += 1

            self.main_info()

    def prev_album(self):

        self.f_a = True

        if self.a_num == 0:
            messagebox.showwarning("Ошибка", "Дальше альбомов нет")
        else:
            for each in self.group_a:
                each.destroy()
            for each in self.group_links:
                each.destroy()
            self.a_num -= 1
            self.page_num_a -= 1
            self.main_info()

    def upload_all(self):

        yandex_uploader = YandexUploader()
        yandex_uploader.upload_all(vk.user_id, self.album_list, vk.album_list[self.a_num][0])
        messagebox.showinfo("Загрузка", yandex_uploader.status)
        # for each in self.group_elements:
        #     each.destroy()
        # for each in self.group_links:
        #     each.destroy()

    def show(self):
        def send(m):
            w = m.widget
            print(w._name)
            yandex_uploader = YandexUploader()
            yandex_uploader.upload_one(vk.user_id,
                                       self.album_list[int(w._name[7:]) - b_first + self.counter],
                                       vk.album_list[self.a_num][0])
            messagebox.showinfo("Загрузка", yandex_uploader.status)

        def hide():
            for each in self.group_links:
                each.destroy()
            self.show_b.config(text="Показать", command=self.show)

        def next_page():
            if vk.album_list[self.a_num][1] <= self.counter + self.on_page:
                messagebox.showwarning("Ошибка", "Дальше фото нет")
            else:
                self.counter += self.on_page
                self.page_num += 1
                for each in self.group_links:
                    each.destroy()
                p_lbl.config(text=f"Стр{self.page_num}")
                self.show()

        def prev_page():
            if self.counter == 0:
                p_lbl.config(text="Стр1")
                messagebox.showwarning("Ошибка", "Дальше фото нет")
            else:
                self.counter -= self.on_page
                self.page_num -= 1
                p_lbl.config(text=f"Стр{self.page_num}")
                for each in self.group_links:
                    each.destroy()
                self.show()

        self.show_b.config(text="Скрыть", command=hide)

        xx = 300
        yy = self.y + 60

        if vk.album_list[self.a_num][1] - self.counter < self.on_page:
            max_on_page = vk.album_list[self.a_num][1] - self.counter
        else:
            max_on_page = self.on_page
        print(self.counter, max_on_page)

        for i in range(self.counter, max_on_page + self.counter):
            for key, value in self.album_list[i].items():
                if (i + 10) % 20 == 0:
                    yy += 120
                    xx = 300
                try:
                    response = requests.get(value)
                    button_image = Image.open(BytesIO(response.content))
                    button_image = button_image.resize((100, 100), Image.ANTIALIAS)
                    button_image = ImageTk.PhotoImage(button_image)
                except UnidentifiedImageError:
                    button_image = None
                root.update()
                sleep(0.2)
                name = Button(image=button_image, text=i)
                name.image = button_image
                name.bind("<Button-1>", send)
                name.place(x=xx, y=yy, width=100, height=100)
                self.group_links.append(name)
                b_last = int(name._name[7:])
                b_first = b_last - max_on_page + 1
                xx += 110
        # print(b_first, b_last)

        if vk.album_list[self.a_num][1] > 20 and self.f_a:
            prev_page_a = Button(text="<<<", bg="grey", font=("Courier", 8), command=prev_page)
            prev_page_a.place(x=1170, y=300, width=50, height=20)
            p_lbl = Label(text=f"Стр{self.page_num}", bg="grey", font=("Courier", 8))
            p_lbl.place(x=1170 + 80, y=300, width=50, height=20)
            next_page_a = Button(text=">>>", bg="grey", font=("Courier", 8), command=next_page)
            next_page_a.place(x=1170 + 80 + 80, y=300, width=50, height=20)
            self.f_a = False

    def main_info(self):
        # print(self.a_num)
        self.album_list = vk.execute_album_link(self.a_num)
        print(len(self.album_list))
        # вот здесь для альбома с индексом a_num собираются ссылки,
        # a_num изменяется, когда мы переключаем альбомы кнопками next_album, prev_album

        font = ("Comic Sans MS", 12)

        if self.first_enter:
            album_count = Label(text=f'Всего альбомов: {vk.album_count}', bg="cyan", font=font)
            album_count.place(x=self.x, y=self.y, width=290, height=50)

        try:
            album_name = Label(text=vk.album_list[self.a_num][0], bg="grey", font=font)
        except TclError:
            album_name = Label(text="ошибка_названия", bg="grey", font=font)
        album_name.place(x=self.x, y=self.y + 60, width=290, height=50)
        photos_count = Label(text=f'Фоток: {vk.album_list[self.a_num][1]}', bg='green', font=font)
        photos_count.place(x=self.x, y=self.y + 120, width=250, height=40)

        self.show_b = Button(text="Показать", bg="green", font=font, command=self.show)
        self.show_b.place(x=self.x, y=self.y + 180, width=250, height=50)
        button_upload_all_a = Button(text="Загрузить все", bg="grey", font=font, command=self.upload_all)
        button_upload_all_a.place(x=self.x, y=self.y + 240, width=250, height=50)
        self.group_a.append(self.show_b)
        self.group_a.append(button_upload_all_a)

        if not self.album_list:
            print('denied')
            denied_lbl = Label(text=vk.error, bg="red", font=("Courier", 18))
            denied_lbl.place(x=350, y=270 + 60 + 30, width=400, height=200)
            self.show_b.destroy()
            button_upload_all_a.destroy()
            self.group_a.append(denied_lbl)

        if vk.album_count > 1 and self.first_enter:
            prev_button_a = Button(text="<<<", bg="grey", font=font, command=self.prev_album)
            prev_button_a.place(x=330, y=self.y, width=50, height=50)

            self.page_lbl.place(x=400, y=self.y, width=120, height=50)
            next_button_a = Button(text=">>>", bg="grey", font=font, command=self.next_album)
            next_button_a.place(x=540, y=self.y, width=50, height=50)
        if not self.first_enter:
            self.page_lbl = Label(text=f"Альбом{self.page_num_a}", bg="grey", font=font)
            self.page_lbl.place(x=400, y=self.y, width=120, height=50)

        self.first_enter = False


class App:
    def __init__(self):
        self.quit_app()
        self.start_again()

        label1 = Label(text="Введите id \nпользователя ВК:", font=("Courier", 20))
        label1.place(x=700 - 125, y=120, width=260, height=150)

        self.data1 = Entry(justify="center", font=("Courier", 22))  # justify - текст по центру
        self.data1.place(x=700 - 150, y=240, width=300, height=75)

        validate_button = Button(text="Проверить ID", bg="green", font=("Courier", 22), command=self.validate)
        validate_button.place(x=700 - 150, y=330, width=300, height=100)

    def quit_app(self):
        def quit_b():
            root.destroy()

        quit_button = Button(text="Выход", bg="coral2", font=("Courier", 10), command=quit_b)
        quit_button.place(x=0, y=600 - 25, width=50, height=25)

    def start_again(self):
        def start_b():
            for each in root.place_slaves():
                each.destroy()
            global vk
            vk = VkPhotos()
            self.__init__()

        start_button = Button(text="Заново", bg="orange", font=("Courier", 10), command=start_b)
        start_button.place(x=50, y=600 - 25, width=50, height=25)

    def validate(self):
        entry_data = self.data1.get()

        if not vk.validate_user_id(entry_data):  # неверный id или ник, или неверный токен
            messagebox.showerror("Ошибка", vk.validate_error)
        else:
            messagebox.showinfo("Успех", 'Успешно введён id пользователя')
            for each in root.place_slaves():
                each.destroy()
            self.quit_app()
            self.start_again()
            # Button(text='инструкция', command=welcome).place(x=0, y=0)
            info_lbl = Label(text=f"{vk.user_id, entry_data}", bg="khaki1", font=("Courier", 10))
            info_lbl.place(x=0, y=0, width=250, height=15)

            self.create()

    def create(self):
        vk.execute_photos_get()  # вот здесь инициировались словари со ссылками для стены и профиля
        vk.get_albums_list()  # здесь инициировался список доступных альбомов, пока без ссылок
        print(vk.user_id)
        print(vk.album_list)
        # если нигде нету фоток, начнём с начала
        if vk.wall_count == 0 and vk.profile_count == 0 and vk.album_count == 0:
            for each in root.place_slaves():
                each.destroy()
            messagebox.showwarning('Дальше бесполезно', 'У этого пользователя ВООБЩЕ нет фоток')
            self.__init__()
            return

        ProfileWall(vk.profile, 'profile', vk.profile_count, 20, on_page=10).main_info()
        ProfileWall(vk.wall, 'wall', vk.wall_count, 150, on_page=10).main_info()

        if vk.album_list:
            Album(vk.album_list[0][2], vk.album_list[0][1], y=270, on_page=20)
        else:
            no_personal_albums = Label(text="нет персональных альбомов\nили они закрыты",
                                       bg="yellow", font=("Courier", 14))
            no_personal_albums.place(x=10, y=270, width=300, height=150)


vk = VkPhotos()

root = Tk()
root.geometry('1400x600+100+100')  # обязательно так, через пробел нельзя
root.resizable(False, False)  # заблокировать фуллскрин

app = App()

root.mainloop()
