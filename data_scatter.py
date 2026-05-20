import dataset
import io
import tkinter
from tkinter import ttk, filedialog
from matplotlib import figure
from PIL import Image, ImageTk
from datetime import datetime

df = dataset.df
counting_cols = dataset.counting_cols

window = tkinter.Tk()
window.title("Точечная диаграмма")
window.geometry("850x520")

image = None

def get_scatter_as_photoImage(x, y):
    fig = figure.Figure(figsize=(6, 4.5), dpi=100)
    ax = fig.add_subplot()
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.scatter(df[x], df[y], marker='>', alpha=0.7, edgecolors='none')
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    return ImageTk.PhotoImage(img)

def update(event=None):
    global image
    x = x_axis.get()
    y = y_axis.get()
    
    if x and y:
        image = get_scatter_as_photoImage(x, y)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tkinter.NW, image=image)

def save():
    x = x_axis.get()
    y = y_axis.get()
    
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
            ax.scatter(df[x], df[y])
            fig.savefig(file_path, dpi=300)

if __name__ == "__main__":

    control_panel = tkinter.Frame(window, padx=15, pady=15)
    control_panel.pack(side=tkinter.LEFT, fill=tkinter.Y)

    tkinter.Label(control_panel, text="Ось X:").pack(anchor=tkinter.W, pady=(0, 2))
    x_axis = ttk.Combobox(control_panel, values=counting_cols, state="readonly", width=20)
    x_axis.pack(pady=(0, 15))
    if counting_cols: x_axis.current(0)


    tkinter.Label(control_panel, text="Ось Y:").pack(anchor=tkinter.W, pady=(0, 2))
    y_axis = ttk.Combobox(control_panel, values=counting_cols, state="readonly", width=20)
    y_axis.pack(pady=(0, 15))
    if len(counting_cols) > 1: y_axis.current(1)


    save_btn = tkinter.Button(control_panel, text="Сохранить", command=save, width=18)
    save_btn.pack()

    canvas = tkinter.Canvas(window, width=600, height=450, bg="white")
    canvas.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True, padx=10, pady=10)

    update()

    x_axis.bind("<<ComboboxSelected>>", update)
    y_axis.bind("<<ComboboxSelected>>", update)

    window.mainloop()