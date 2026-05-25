import dataset
import io
import tkinter
import pandas
import matplotlib
from tkinter import ttk, filedialog
from matplotlib import figure
from PIL import Image, ImageTk
from datetime import datetime

df = dataset.df
df = df.fillna('')
cols = df.columns.tolist()
counting_cols = dataset.counting_cols
categorical_cols = dataset.categorical_cols

window = tkinter.Tk()
window.title("Точечная диаграмма")
window.geometry("850x520")

image = None

def get_scatter_as_photoImage(x, y, cmap_name):
    fig = figure.Figure(figsize=(6, 4.5), dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    
    is_x_num = x in counting_cols
    is_y_num = y in counting_cols
    is_x_cat = x in categorical_cols
    is_y_cat = y in categorical_cols

    try:
        cmap = matplotlib.colormaps[cmap_name]
    except:
        cmap = matplotlib.colormaps["plasmas"]

    # Гистограмма
    if x == y and is_x_num:
        n, bins, patches = ax.hist(df[x].dropna(), bins=10, edgecolor='black', linewidth=0.5)
        for i, patch in enumerate(patches):
            patch.set_facecolor(cmap(i / len(patches)))

        ax.set_xlabel(x)
        ax.set_ylabel("Количество")


    # Круговая диаграмма
    elif x == y and is_x_cat:
        counts = df[x].value_counts()
        colors = [cmap(i / max(1, len(counts)-1)) for i in range(len(counts))]
        ax.pie(
            counts, 
            labels=counts.index, 
            autopct='%1.1f%%', 
            colors=colors,
            wedgeprops={'edgecolor': 'black', 'linewidth': 0.5}
        )


    # Столбчатая диаграмма
    elif is_x_cat:
        counts = df[x].value_counts()
        colors = [cmap(i / max(1, len(counts)-1)) for i in range(len(counts))]
        ax.bar(counts.index.astype(str), counts.values, color=colors, edgecolor='black')
        ax.set_xlabel(x)
        ax.set_ylabel("Количество записей")
        ax.tick_params(axis='x', rotation=45, labelsize=9)


    # Коробчатая диаграмма
    elif is_x_num and is_y_cat:
        categories = df[y].dropna().unique()
        data_to_plot = [df[df[y] == cat][x].dropna().values for cat in categories]
        bp = ax.boxplot(data_to_plot, vert=False, tick_labels=categories, patch_artist=True)

        for i, box in enumerate(bp['boxes']):
            box.set_facecolor(cmap(i / max(1, len(categories)-1)))
            box.set_edgecolor('black')
            box.set_linewidth(0.8)
            
        ax.set_xlabel(x)
        ax.set_ylabel(y)


    # Точечная диаграмма
    else:
        try:
            color_data = pandas.to_numeric(df[y])
        except Exception:
            color_data = range(len(df))
            
        ax.scatter(df[x], df[y], c=color_data, cmap=cmap_name, marker='>', alpha=0.7, edgecolors='none')
        ax.set_xlabel(x)
        ax.set_ylabel(y)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img = Image.open(buf)
    photo_img = ImageTk.PhotoImage(img)
    return photo_img, fig



def update(event=None):
    global image
    x = x_axis.get()
    y = y_axis.get()
    selected_cmap = cmap_select.get()
    
    if x and y:
        global image
        canvas.delete("all")
        # Принимаем оба значения, но fig здесь просто игнорируем
        image, _ = get_scatter_as_photoImage(x, y, selected_cmap)
        canvas.create_image(0, 0, anchor=tkinter.NW, image=image)
        canvas.update_idletasks()


def save():
    x = x_axis.get()
    y = y_axis.get()
    selected_cmap = cmap_select.get()
    
    if x and y:
        now = datetime.now()
        default_filename = now.strftime("graph%H_%M_%S.png")
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")]
        )
        
        if file_path:
            _, fig_to_save = get_scatter_as_photoImage(x, y, selected_cmap)
            fig_to_save.savefig(file_path, dpi=300)



if __name__ == "__main__":
    control_panel = tkinter.Frame(window, padx=15, pady=15)
    control_panel.pack(side=tkinter.LEFT, fill=tkinter.Y)

    tkinter.Label(control_panel, text="Ось X:").pack(anchor=tkinter.W, pady=(0, 2))
    x_axis = ttk.Combobox(control_panel, values=cols, state="readonly", width=20)
    x_axis.pack(pady=(0, 15))
    if cols: x_axis.current(0)

    tkinter.Label(control_panel, text="Ось Y:").pack(anchor=tkinter.W, pady=(0, 2))
    y_axis = ttk.Combobox(control_panel, values=cols, state="readonly", width=20)
    y_axis.pack(pady=(0, 15))
    if len(cols) > 1: y_axis.current(1)

    cmap_options = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'winter','PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'spring', 'summer', 'autumn']
    tkinter.Label(control_panel, text="Цветовая схема:").pack(anchor=tkinter.W, pady=(0, 2))
    cmap_select = ttk.Combobox(control_panel, values=cmap_options, state="readonly", width=20)
    cmap_select.pack(pady=(0, 15))
    cmap_select.current(1)

    save_btn = tkinter.Button(control_panel, text="Сохранить", command=save, width=18)
    save_btn.pack()

    canvas = tkinter.Canvas(window, width=600, height=450, bg="white")
    canvas.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True, padx=10, pady=10)

    update()

    x_axis.bind("<<ComboboxSelected>>", update)
    y_axis.bind("<<ComboboxSelected>>", update)
    cmap_select.bind("<<ComboboxSelected>>", update)

    window.mainloop()