import requests
import json
import sqlite3
import tkinter as tk
from tkinter import *
import tkinter.messagebox
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

global img


def get_anime_data(conn,label, status, status_bar):
    url = "https://api.jikan.moe/v3/top/anime/1/airing"

    try:
        response = requests.request("GET", url)
        if str(response) == "<Response [200]>":
            response_text = response.text
            response_json = json.loads(response_text)

            top = response_json['top']

            try:
                cursor = conn.cursor()
                cursor.execute("""CREATE TABLE IF NOT EXISTS anime(
                                id INT PRIMARY KEY,
                                title TEXT,
                                members INT,
                                episodes INT);
                """)
                conn.commit()

                animes_list = []
                for item in top:
                    anime_id = str(item['rank'])
                    title = item['title']
                    members = str(item['members'])
                    episodes = str(item['episodes'])

                    anime = (anime_id, title, members, episodes)
                    animes_list.append(anime)

                cursor.executemany("""
                            INSERT INTO anime VALUES(?, ?, ?, ?);
                            """, animes_list)
                conn.commit()
                status.set("New records are obtained")
                status_bar.update()
            except sqlite3.IntegrityError:
                print("Tables already exist")
        else:
            label.config(text="Your request was not correct. Please Check it")
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def clear_db(conn, status, status_bar):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE anime")
        conn.commit()
        status.set("Old Table is deleted ")
        status_bar.update()
    except sqlite3.OperationalError:
        print("No Tables to Delete")


def average_episode_number(conn, label, status, status_bar):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT avg(episodes) FROM anime')
        avg_episodes = "Average Number of Episodes " + str(int(cursor.fetchone()[0]))
        label.config(text=avg_episodes)
        status.set("Average Number is Prepared")
        status_bar.update()
    except sqlite3.OperationalError:
        label.config(text="Please Upload your data")


def top_chart(conn, canvas, status, status_bar):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT title, members FROM anime LIMIT 5')
        table_list = cursor.fetchall()
        title_list = []
        members_list = []
        for item in table_list:
            title_list.append(item[0])
            members_list.append(item[1])
        data = {'title': title_list,
                'members': members_list}
        df = pd.DataFrame(data, columns=['title', 'members'])

        new_colors = ['green', 'blue', 'purple', 'brown', 'teal', 'red', 'blue', 'yellow']
        plt.rcParams["figure.figsize"] = (23, 8)
        plt.bar(df['title'], df['members'], color=new_colors)
        plt.title('Title vs Members', fontsize=14)
        plt.xlabel('Title', fontsize=14)
        plt.ylabel('Members', fontsize=14)
        plt.savefig('chart.png')
        image = Image.open('chart.png')
        image.thumbnail((1500, 1500))
        image.save('image_thumbnail.png')
        global img
        img = PhotoImage(file='image_thumbnail.png')
        canvas.create_image(700, 300, image=img)

        status.set("Chart Created")
        status_bar.update()
    except sqlite3.OperationalError:
        canvas.delete('all')


def change_fonts(label, label_1, status, status_bar, btn_avg, btn_chart):
    label.config(font="Helvetica")
    label.pack()

    label_1.config(font="Helvetica")
    label_1.pack()

    btn_avg.config(font="Helvetica", fg='purple')
    btn_avg.pack()

    btn_chart.config(font="Helvetica", fg='purple')
    btn_chart.pack()

    status.set("Fonts Changed")
    status_bar.update()


def top_anime(conn):
    main_window = Tk()
    main_window.title("Top 50 Airing Animes")
    main_window.geometry('1980x1080')
    frame = Frame(main_window)
    frame.pack()
    label = Label(main_window, text="Some Calculations", fg="purple", font=("Comic Sans MS", 15, "bold"))
    label.pack()
    status = StringVar()
    status.set('Ready')
    status_bar = Label(main_window, textvariable=status, relief=SUNKEN)
    status_bar.pack(side=BOTTOM, fill=X)
    btn_avg = tk.Button(master=main_window,
                        text="Show Average Number of Episodes",
                        command=lambda: average_episode_number(conn, label, status, status_bar))
    btn_avg.pack()
    label_1 = Label(main_window, text="Draw Bar Chart", fg="purple", font=("Comic Sans MS", 15, "bold"))
    label_1.pack()
    canvas = Canvas(main_window, height=600, width=1500)
    canvas.pack()
    btn_chart = tk.Button(master=main_window,
                          text="Plot A Bar Chart",
                          command=lambda: top_chart(conn, canvas, status, status_bar))
    btn_chart.pack()
    menubar = Menu(main_window)
    main_window.config(menu=menubar)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Clear Previous Records", command=lambda: clear_db(conn, status, status_bar))
    file_menu.add_command(label="Get Top Airing List", command=lambda: get_anime_data(conn,label, status, status_bar))
    file_menu.add_command(label="Change Fonts", command=lambda: change_fonts(label, label_1, status, status_bar,
                                                                             btn_avg, btn_chart))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=lambda: exit_app())
    menubar.add_cascade(label="File", menu=file_menu)
    main_window.mainloop()


def exit_app():
    answer = tk.messagebox.askyesno(
        title="Exit",
        message="Do you really want to quit?")
    if answer is True:
        exit()


def run():
    conn = sqlite3.connect("q.db")
    top_anime(conn)


if __name__ == "__main__":
    run()
