import dataset
import io
import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from datetime import datetime
import pandas
from tkinter import colorchooser

df = dataset.df
df = df.fillna(0)
cols = df.columns.tolist()
counting_cols = dataset.counting_cols
categorical_cols = dataset.categorical_cols

DEFAULT_THICKNESS = 6
DEFAULT_COLOR = "#162511"

window = tk.Tk()
window.title("Диаграмма")
window.geometry("1200x800")

image = None
fig_global = None
lines_history = []
canvas_objects_history = []
undo_disabled = False
current_line_points = []
current_canvas_objects = []
all_cols = counting_cols + categorical_cols
selected_x = all_cols[0] if all_cols else ""
selected_y = all_cols[1] if len(all_cols) > 1 else (all_cols[0] if all_cols else "")
x_buttons = {}
y_buttons = {}


def select_x_axis(col_name):
    global selected_x, lines_history, canvas_objects_history
    selected_x = col_name
    lines_history.clear()
    canvas_objects_history.clear()
    update()
    disable_draw_mode()


def select_y_axis(col_name):
    global selected_y, lines_history, canvas_objects_history
    selected_y = col_name
    lines_history.clear()
    canvas_objects_history.clear()
    update()
    disable_draw_mode()


def get_scatter_as_photoImage(x, y, cmap_name, width=600, height=450):
    global fig_global
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
        
    # Гистограмма
    if x == y and is_x_num:
        n, bins, patches = ax.hist(df[x].dropna(), bins=10, edgecolor='black', linewidth=0.5)
        for i, patch in enumerate(patches):
            patch.set_facecolor(cmap(i / max(1, len(patches)-1)))
        ax.set_xlabel(x)
        ax.set_ylabel("Количество")
        
    # Круговая диаграмма
    elif x == y and is_x_cat:
        counts = df[x].value_counts()
        colors = [cmap(i / max(1, len(counts)-1)) for i in range(len(counts))]
        ax.pie(
            counts, labels=counts.index, autopct='%1.1f%%', colors=colors,
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
            
        ax.scatter(df[x], df[y], c=color_data, cmap=cmap, marker='>', alpha=0.7, edgecolors='none')
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        
    fig.tight_layout()
    fig_global = fig
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    img = Image.open(buf)
    photo_img = ImageTk.PhotoImage(img)
    return photo_img, fig


def start_draw(event):
    if not is_drawing_mode.get():
        return
    global current_line_points, current_canvas_objects
    
    c_width = max(canvas.winfo_width(), 10)
    c_height = max(canvas.winfo_height(), 10)
    
    current_line_points = [(event.x / c_width, event.y / c_height)]
    current_canvas_objects = []

def do_draw(event):
    if not is_drawing_mode.get():
        return
    global current_line_points, current_canvas_objects
    
    c_width = max(canvas.winfo_width(), 10)
    c_height = max(canvas.winfo_height(), 10)
    
    if current_line_points:
        prev_x = current_line_points[-1][0] * c_width
        prev_y = current_line_points[-1][1] * c_height
        
        try:
            thick = int(current_thickness.get())
        except Exception:
            thick = DEFAULT_THICKNESS
            
        color = current_color.get()
        
        obj_id = canvas.create_line(
            prev_x, prev_y, event.x, event.y,
            fill=color, width=thick, capstyle=tk.ROUND, smooth=True
        )
        current_canvas_objects.append(obj_id)
        current_line_points.append((event.x / c_width, event.y / c_height))

def stop_draw(event):
    if not is_drawing_mode.get():
        return
    global lines_history, canvas_objects_history, undo_disabled, current_line_points, current_canvas_objects
    
    if len(current_line_points) > 1:
        lines_history.append({
            'points': current_line_points, 
            'color': current_color.get(), 
            'width': current_thickness.get()
        })
        canvas_objects_history.append(current_canvas_objects)
        undo_disabled = False  
        
    current_line_points = []
    current_canvas_objects = []


def undo(event=None):
    global lines_history, canvas_objects_history, undo_disabled
    
    if event and hasattr(event, 'keysym'):
        is_ctrl = (event.state & 4) != 0
        is_z_key = (event.keysym.lower() == 'z') or (event.keycode == 90)
        if not (is_ctrl and is_z_key):
            return

    if undo_disabled or current_line_points:
        return "break"
        
    if lines_history and canvas_objects_history:
        lines_history.pop()
        last_line_rendered = canvas_objects_history.pop()
        for obj_id in last_line_rendered:
            canvas.delete(obj_id)
        canvas.update_idletasks()
    
    undo_disabled = True
        
    return "break"


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
        
        for line in lines_history:
            prev_pt = None
            for pt in line['points']:
                curr_x = pt[0] * canvas_width
                curr_y = pt[1] * canvas_height
                if prev_pt:
                    canvas.create_line(prev_pt[0], prev_pt[1], curr_x, curr_y, fill=line['color'], width=line['width'], capstyle=tk.ROUND, smooth=True)
                prev_pt = (curr_x, curr_y)
                
        canvas.update_idletasks()


def save():
    x = selected_x
    y = selected_y
    
    try:
        selected_cmap = cmap_select.get()
    except NameError:
        selected_cmap = "plasma"
        
    if x and y:
        now = datetime.now()
        default_filename = now.strftime("graph%H_%M_%S.png")
        
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")]
        )
        
        if file_path:
            _, fig_to_save = get_scatter_as_photoImage(x, y, selected_cmap, 600, 450)
            ax_to_save = fig_to_save.gca()
            
            for line in lines_history:
                xs = [pt[0] for pt in line['points']]
                ys = [1 - pt[1] for pt in line['points']]
                
                ax_to_save.plot(xs, ys, 
                    color=line['color'], 
                    linewidth=line['width'] / 2, 
                    transform=fig_to_save.transFigure
                )
                
            fig_to_save.savefig(file_path, dpi=300)


if __name__ == "__main__":
    window.rowconfigure(0, weight=1)
    window.rowconfigure(1, weight=0)
    window.columnconfigure(0, weight=0)
    window.columnconfigure(1, weight=1)

    is_drawing_mode = tk.BooleanVar(value=False)
    current_color = tk.StringVar(value=DEFAULT_COLOR)
    current_thickness = tk.IntVar(value=DEFAULT_THICKNESS)

    control_panel = tk.Frame(window, padx=15, pady=15)
    control_panel.grid(row=0, column=0, sticky="ns")

    y_btn_frame = tk.Frame(control_panel)
    y_btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

    tk.Label(y_btn_frame, text="Ось Y (Категории):", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(0, 5))
    
    for col in all_cols:
        btn = tk.Button(y_btn_frame, text=col, width=18, anchor="w", command=lambda c=col: select_y_axis(c), font=("Arial", 9))
        btn.pack(fill=tk.X, pady=2)
        y_buttons[col] = btn

    settings_frame = tk.Frame(control_panel, padx=10)
    settings_frame.pack(side=tk.LEFT, fill=tk.Y)

    def toggle_draw_mode():
        if is_drawing_mode.get():
            is_drawing_mode.set(False)
            draw_btn.config(relief=tk.RAISED, bg="SystemButtonFace")
            window.config(cursor="")

        else:
            is_drawing_mode.set(True)
            draw_btn.config(relief=tk.SUNKEN, bg="lightgray")
            window.config(cursor="pencil")

    def disable_draw_mode(event=None):
        is_drawing_mode.set(False)
        draw_btn.config(relief=tk.RAISED, bg="SystemButtonFace")
        window.config(cursor="")

    draw_btn = tk.Button(settings_frame, text="Рисование", command=toggle_draw_mode, font=("Arial", 9, "bold"), width=15)
    draw_btn.pack(anchor=tk.W, pady=(0, 10))

    tk.Label(settings_frame, text="Толщина:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 2))
    thick_entry = tk.Entry(settings_frame, textvariable=current_thickness, width=15)
    thick_entry.pack(anchor=tk.W, pady=(0, 10))

    def choose_color():
        color_code = colorchooser.askcolor(title="Выбор цвета")
        if color_code:
            current_color.set(color_code)
            color_block.config(bg=color_code)

    tk.Label(settings_frame, text="Цвет кисти:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 2))
    color_block = tk.Button(settings_frame, bg=current_color.get(), width=12, command=choose_color)
    color_block.pack(anchor=tk.W, pady=(0, 15))

    tk.Frame(settings_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)

    cmap_options = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'winter']
    tk.Label(settings_frame, text="Схема графика:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5, 2))
    
    cmap_select = ttk.Combobox(settings_frame, values=cmap_options, state="readonly", width=13)
    cmap_select.pack(pady=(0, 15))
    cmap_select.current(1)
    cmap_select.bind("<<ComboboxSelected>>", update)

    save_btn = tk.Button(settings_frame, text="Сохранить", command=save, width=15, bg="#ffc107")
    save_btn.pack(side=tk.BOTTOM, pady=(20, 0))

    canvas = tk.Canvas(window, bg="white")
    canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    canvas.bind("<Button-1>", start_draw)
    canvas.bind("<Button-3>", disable_draw_mode)
    canvas.bind("<B1-Motion>", do_draw)
    canvas.bind("<ButtonRelease-1>", stop_draw)
    window.bind("<KeyPress>", undo)
    canvas.focus_set()

    x_panel = tk.Frame(window, padx=15, pady=10)
    x_panel.grid(row=1, column=1, sticky="ew")
    
    tk.Label(x_panel, text="Ось X (Категории):", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(0, 5))
    
    x_buttons_frame = tk.Frame(x_panel)
    x_buttons_frame.pack(fill=tk.X)
    
    max_columns = 3
    for index, col in enumerate(all_cols):
        row_idx = index // max_columns
        col_idx = index % max_columns
        
        btn = tk.Button(x_buttons_frame, text=col, command=lambda c=col: select_x_axis(c), font=("Arial", 8), wraplength=150)
        btn.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="ew")
        x_buttons_frame.columnconfigure(col_idx, weight=1)
        x_buttons[col] = btn

    if all_cols:
        select_x_axis(selected_x)
        select_y_axis(selected_y)

    canvas.bind("<Configure>", update)
    cmap_select.bind("<<ComboboxSelected>>", lambda e: (update(), disable_draw_mode()))

    window.mainloop()