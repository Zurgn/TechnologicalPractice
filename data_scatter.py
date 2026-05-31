import dataset
import io
import tkinter
from tkinter import filedialog
from matplotlib import figure
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from datetime import datetime

df = dataset.df
counting_cols = dataset.counting_cols

image = None
fig_global = None

def get_scatter_as_photoImage(x, y, width=600, height=450):
    global fig_global
    dpi = 100
    fig_width = max(width / dpi, 2.0)
    fig_height = max(height / dpi, 2.0)

    fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.scatter(df[x], df[y], marker='>', alpha=0.7, edgecolors='none')
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    return ImageTk.PhotoImage(img)

def save():
    global selected_x, selected_y
    x = selected_x
    y = selected_y
    
    if x and y:
        now = datetime.now()
        default_filename = now.strftime("graph%H_%M_%S.png")
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")]
        )
        
        if file_path:
            fig = figure.Figure()
            ax = fig.add_subplot()
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.scatter(df[x], df[y], marker='>', alpha=0.7, edgecolors='none')
            fig.tight_layout()
            fig.savefig(file_path, dpi=300)

selected_x = counting_cols[0]
selected_y = counting_cols[1]

x_buttons = {}
y_buttons = {}

def update(event=None):
    global image
    x = selected_x
    y = selected_y
    
    if x and y:
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width < 10: canvas_width = 600
        if canvas_height < 10: canvas_height = 450

        image = get_scatter_as_photoImage(x, y, canvas_width, canvas_height)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tkinter.NW, image=image)

def select_x_axis(col_name):
    global selected_x
    selected_x = col_name
    update()

def select_y_axis(col_name):
    global selected_y
    selected_y = col_name
    update()


if __name__ == "__main__":
    window = tkinter.Tk()
    window.title("Диаграмма")
    window.geometry("1200x800")
    window.resizable(False, False)

    window.rowconfigure(0, weight=1)
    window.rowconfigure(1, weight=0)
    window.columnconfigure(0, weight=0)
    window.columnconfigure(1, weight=1)

    y_panel = tkinter.Frame(window, padx=10, pady=10)
    y_panel.grid(row=0, column=0, sticky="ns")
    tkinter.Label(y_panel, text="Ордината:", font=("Arial", 10, "bold")).pack(anchor=tkinter.W, pady=(0, 5))
    
    for col in counting_cols:
        btn = tkinter.Button(y_panel, text=col, width=18, anchor="w", command=lambda c=col: select_y_axis(c))
        btn.pack(fill=tkinter.X, pady=2)
        y_buttons[col] = btn

    canvas = tkinter.Canvas(window, width=600, height=450, bg="white")
    canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    x_panel = tkinter.Frame(window, padx=10, pady=10)
    x_panel.grid(row=1, column=1, sticky="ew")
    tkinter.Label(x_panel, text="Абсцисса:", font=("Arial", 10, "bold")).pack(anchor=tkinter.W, pady=(0, 5))
    
    x_buttons_frame = tkinter.Frame(x_panel)
    x_buttons_frame.pack(fill=tkinter.X)
    
    max_columns = 3
    for index, col in enumerate(counting_cols):
        row_idx = index // max_columns
        col_idx = index % max_columns
        
        btn = tkinter.Button(x_buttons_frame, text=col, command=lambda c=col: select_x_axis(c), font=("Arial", 9), wraplength=150)
        btn.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="ew")
        x_buttons_frame.columnconfigure(col_idx, weight=1)
        x_buttons[col] = btn

    save_btn = tkinter.Button(y_panel, text="Сохранить", command=save, width=18)
    save_btn.pack(side=tkinter.BOTTOM, pady=(20, 0))

    if counting_cols:
        select_x_axis(selected_x)
        select_y_axis(selected_y)

    canvas.bind("<Configure>", update)

    window.mainloop()