import dataset
import io
import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from datetime import datetime
import matplotlib
import pandas

df = dataset.df
df = df.fillna(0)
cols = df.columns.tolist()
counting_cols = dataset.counting_cols
categorical_cols = dataset.categorical_cols

window = tk.Tk()
window.title("Диаграмма")
window.geometry("1000x1000")

image = None
fig_global = None

all_cols = counting_cols + categorical_cols
selected_x = all_cols[0] if all_cols else ""
selected_y = all_cols[1] if len(all_cols) > 1 else (all_cols[0] if all_cols else "")

x_buttons = {}
y_buttons = {}

def select_x_axis(col_name):
    global selected_x
    selected_x = col_name
    update()

def select_y_axis(col_name):
    global selected_y
    selected_y = col_name
    update()

def get_scatter_as_photoImage(x, y, cmap_name, width=600, height=450):
    dpi = 100
    fig_width = max(width / dpi, 2.0)
    fig_height = max(height / dpi, 2.0)
    
    fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)
    
    is_x_num = x in counting_cols
    is_y_num = y in counting_cols
    is_x_cat = x in categorical_cols
    is_y_cat = y in categorical_cols
    
    try:
        cmap = matplotlib.colormaps[cmap_name]
    except Exception:
        cmap = matplotlib.colormaps["plasma"]
        
    if x == y and is_x_num:
        n, bins, patches = ax.hist(df[x].dropna(), bins=10, edgecolor='black', linewidth=0.5)
        for i, patch in enumerate(patches):
            patch.set_facecolor(cmap(i / max(1, len(patches)-1)))
        ax.set_xlabel(x)
        ax.set_ylabel("Количество")
        
    elif x == y and is_x_cat:
        counts = df[x].value_counts()
        colors = [cmap(i / max(1, len(counts)-1)) for i in range(len(counts))]
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=colors,
               wedgeprops={'edgecolor': 'black', 'linewidth': 0.5})
               
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
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    img = Image.open(buf)
    photo_img = ImageTk.PhotoImage(img)
    return photo_img, fig

def update(event=None):
    global image, fig_global
    x = selected_x
    y = selected_y
    
    try:
        selected_cmap = cmap_select.get()
    except NameError:
        selected_cmap = "plasma"
    
    if x and y:
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width < 10: canvas_width = 600
        if canvas_height < 10: canvas_height = 450
        
        photo_img, fig = get_scatter_as_photoImage(x, y, selected_cmap, canvas_width, canvas_height)
        image = photo_img
        fig_global = fig
        
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=image)
        canvas.update_idletasks()

def save():
    x = selected_x
    y = selected_y
    
    if x and y and fig_global:
        now = datetime.now()
        default_filename = now.strftime("graph%H_%M_%S.png")
        file_path = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")])
        if file_path:
            fig_global.savefig(file_path, dpi=300)

if __name__ == "__main__":
    window.rowconfigure(0, weight=1)
    window.rowconfigure(1, weight=0)
    window.columnconfigure(0, weight=0)
    window.columnconfigure(1, weight=1)

    control_panel = tk.Frame(window, padx=15, pady=15)
    control_panel.grid(row=0, column=0, sticky="ns")

    tk.Label(control_panel, text="Ордината:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
    
    for col in all_cols:
        btn = tk.Button(control_panel, text=col, width=20, anchor="w", command=lambda c=col: select_y_axis(c), font=("Arial", 9), wraplength=140)
        btn.pack(fill=tk.X, pady=2)
        y_buttons[col] = btn

    tk.Frame(control_panel, height=15).pack()
    cmap_options = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'winter']
    tk.Label(control_panel, text="Цветовая схема:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
    
    cmap_select = ttk.Combobox(control_panel, values=cmap_options, state="readonly", width=18)
    cmap_select.pack(pady=(0, 15))
    cmap_select.current(1)
    cmap_select.bind("<<ComboboxSelected>>", update)

    save_btn = tk.Button(control_panel, text="Сохранить", command=save, width=18)
    save_btn.pack(side=tk.BOTTOM, pady=(20, 0))

    canvas = tk.Canvas(window, bg="white")
    canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    x_panel = tk.Frame(window, padx=15, pady=10)
    x_panel.grid(row=1, column=1, sticky="ew")
    
    tk.Label(x_panel, text="Абсцисса:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
    
    x_buttons_frame = tk.Frame(x_panel)
    x_buttons_frame.pack(fill=tk.X)
    
    max_columns = 3
    for index, col in enumerate(all_cols):
        row_idx = index // max_columns
        col_idx = index % max_columns
        btn = tk.Button(x_buttons_frame, text=col, command=lambda c=col: select_x_axis(c), font=("Arial", 9), wraplength=150)
        btn.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="ew")
        x_buttons_frame.columnconfigure(col_idx, weight=1)
        x_buttons[col] = btn

    if selected_x: select_x_axis(selected_x)
    if selected_y: select_y_axis(selected_y)
    canvas.bind("<Configure>", update)

    window.mainloop()