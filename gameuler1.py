import tkinter as tk
from tkinter import colorchooser
import random


# =========================
# WINDOW
# =========================

window = tk.Tk()
window.title("Snake Game")
window.geometry("900x700")
window.minsize(500, 500)
window.configure(bg="black")


# =========================
# CANVAS
# =========================

canvas = tk.Canvas(
    window,
    bg="#000000",
    highlightthickness=0
)

canvas.pack(
    fill="both",
    expand=True
)

window.focus_force()


# =========================
# GAME VARIABLES
# =========================

GRID_SIZE = 30

snake = []
food = []

direction = "Right"
direction_queue = []

score = 0
high_score = 0

game_state = "menu"

after_id = None
resize_after_id = None
countdown_after_id = None

countdown_value = 0
countdown_callback = None

last_result_won = False

fullscreen = False

menu_index = 0
menu_items = []


# =========================
# COLORS
# =========================

head_color = "#00FF00"
body_start_color = "#00CC00"
body_end_color = "#006600"

DEFAULT_HEAD = "#00FF00"
DEFAULT_BODY_START = "#00CC00"
DEFAULT_BODY_END = "#006600"


# =========================
# COLOR FUNCTIONS
# =========================

def hex_to_rgb(color):

    color = color.lstrip("#")

    return (
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16)
    )


def rgb_to_hex(rgb):

    return "#{:02X}{:02X}{:02X}".format(
        int(rgb[0]),
        int(rgb[1]),
        int(rgb[2])
    )


def interpolate_color(color1, color2, amount):

    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    r = r1 + (r2 - r1) * amount
    g = g1 + (g2 - g1) * amount
    b = b1 + (b2 - b1) * amount

    return rgb_to_hex((r, g, b))


# =========================
# ARENA SIZE
# =========================

def get_arena_size():

    width = canvas.winfo_width()
    height = canvas.winfo_height()

    margin = 40

    available_width = width - margin * 2
    available_height = height - margin * 2

    size = min(
        available_width,
        available_height
    )

    return max(size, 1)


def get_arena_position():

    width = canvas.winfo_width()
    height = canvas.winfo_height()

    size = get_arena_size()

    x = (width - size) / 2
    y = (height - size) / 2

    return x, y, size


# =========================
# DRAW ARENA
# =========================

def draw_arena():

    x0, y0, size = get_arena_position()

    canvas.create_rectangle(
        x0,
        y0,
        x0 + size,
        y0 + size,
        outline="#FFFFFF",
        width=4
    )


# =========================
# FOOD
# =========================

INITIAL_FOOD_COUNT = 8
MIN_FOOD_COUNT = 1
FOOD_TAPER_STEP = 20


def get_food_target():

    growth = max(
        0,
        len(snake) - 3
    )

    target = INITIAL_FOOD_COUNT - growth // FOOD_TAPER_STEP

    target = max(MIN_FOOD_COUNT, target)

    free_cells = GRID_SIZE * GRID_SIZE - len(snake)

    return max(
        0,
        min(target, free_cells)
    )


def get_free_cells():

    occupied = set(snake) | set(food)

    return [
        (x, y)
        for x in range(GRID_SIZE)
        for y in range(GRID_SIZE)
        if (x, y) not in occupied
    ]


def maintain_food():

    target = get_food_target()

    if len(food) > target:

        del food[target:]

        return

    if len(food) >= target:

        return

    needed = target - len(food)

    free_cells = get_free_cells()

    random.shuffle(free_cells)

    food.extend(free_cells[:needed])


def initialize_food():

    food.clear()

    maintain_food()


# =========================
# RESET SNAKE
# =========================

def reset_snake():

    global direction
    global score

    center = GRID_SIZE // 2

    snake.clear()

    snake.extend([
        (center, center),
        (center - 1, center),
        (center - 2, center)
    ])

    direction = "Right"

    direction_queue.clear()

    score = 0


# =========================
# SPEED
# =========================

def get_speed():

    return max(
        150 - score,
        90
    )


# =========================
# DRAW GAME
# =========================

def draw_game():

    canvas.delete("all")

    draw_arena()

    x0, y0, arena_size = get_arena_position()

    cell = arena_size / GRID_SIZE


    # =========================
    # FOOD
    # =========================

    for fx, fy in food:

        x1 = x0 + fx * cell
        y1 = y0 + fy * cell

        x2 = x1 + cell
        y2 = y1 + cell

        canvas.create_rectangle(
            x1 + cell * 0.15,
            y1 + cell * 0.15,
            x2 - cell * 0.15,
            y2 - cell * 0.15,
            fill="#FF0000",
            outline=""
        )


    # =========================
    # SNAKE
    # =========================

    snake_length = len(snake)

    for i, (sx, sy) in enumerate(snake):

        x1 = x0 + sx * cell
        y1 = y0 + sy * cell

        x2 = x1 + cell
        y2 = y1 + cell

        if i == 0:

            color = head_color

        else:

            if snake_length <= 2:

                amount = 1

            else:

                amount = (i - 1) / (snake_length - 2)

            color = interpolate_color(
                body_start_color,
                body_end_color,
                amount
            )

        canvas.create_rectangle(
            x1 + cell * 0.08,
            y1 + cell * 0.08,
            x2 - cell * 0.08,
            y2 - cell * 0.08,
            fill=color,
            outline=""
        )

        if i == 0:

            draw_eyes(
                x1,
                y1,
                cell
            )


    # =========================
    # SCORE
    # =========================

    canvas.create_text(
        x0,
        y0 - 15,
        text=f"SCORE: {score}    HIGH SCORE: {high_score}",
        fill="white",
        font=("Arial", 14, "bold"),
        anchor="sw"
    )


# =========================
# EYES
# =========================

def draw_eyes(x1, y1, cell):

    eye_radius = cell * 0.09

    forward_offset = cell * 0.22
    side_offset = cell * 0.20

    cx = x1 + cell / 2
    cy = y1 + cell / 2

    if direction == "Up":

        eye1 = (cx - side_offset, cy - forward_offset)
        eye2 = (cx + side_offset, cy - forward_offset)

    elif direction == "Down":

        eye1 = (cx - side_offset, cy + forward_offset)
        eye2 = (cx + side_offset, cy + forward_offset)

    elif direction == "Left":

        eye1 = (cx - forward_offset, cy - side_offset)
        eye2 = (cx - forward_offset, cy + side_offset)

    else:

        eye1 = (cx + forward_offset, cy - side_offset)
        eye2 = (cx + forward_offset, cy + side_offset)

    for ex, ey in (eye1, eye2):

        canvas.create_oval(
            ex - eye_radius,
            ey - eye_radius,
            ex + eye_radius,
            ey + eye_radius,
            fill="black",
            outline=""
        )


# =========================
# PAUSE BUTTON
# =========================

pause_frame = tk.Frame(
    window,
    bg="black"
)

pause_button = tk.Button(
    pause_frame,
    text="PAUSE",
    command=lambda: pause_game(),
    bg="black",
    fg="white",
    activebackground="black",
    activeforeground="#00FF00",
    font=("Arial", 12, "bold"),
    relief="flat",
    bd=0
)

pause_button.pack()

pause_label = tk.Label(
    pause_frame,
    text="ESC = PAUSE / RESUME",
    bg="black",
    fg="#777777",
    font=("Arial", 9)
)

pause_label.pack()


def show_pause_button():

    if not pause_frame.winfo_ismapped():

        pause_frame.pack(
            side="bottom",
            pady=(0, 10)
        )

    window.update_idletasks()


def hide_pause_button():

    pause_frame.pack_forget()

    window.update_idletasks()


# =========================
# TIMER
# =========================

def cancel_timer():

    global after_id

    if after_id is not None:

        try:
            window.after_cancel(after_id)

        except:
            pass

        after_id = None


def schedule_move():

    global after_id

    cancel_timer()

    after_id = window.after(
        get_speed(),
        move_snake
    )


# =========================
# COUNTDOWN
# =========================

def cancel_countdown_timer():

    global countdown_after_id

    if countdown_after_id is not None:

        try:
            window.after_cancel(countdown_after_id)

        except:
            pass

        countdown_after_id = None


def start_countdown(callback):

    global game_state
    global countdown_value
    global countdown_callback

    cancel_timer()
    cancel_countdown_timer()

    game_state = "countdown"

    countdown_callback = callback
    countdown_value = 3

    tick_countdown()


def tick_countdown():

    global countdown_after_id

    if game_state != "countdown":

        return

    if countdown_value <= 0:

        callback = countdown_callback

        callback()

        return

    draw_countdown()

    countdown_after_id = window.after(
        1000,
        advance_countdown
    )


def advance_countdown():

    global countdown_value

    countdown_value -= 1

    tick_countdown()


def draw_countdown():

    draw_game()

    x0, y0, arena_size = get_arena_position()

    cx = x0 + arena_size / 2
    cy = y0 + arena_size / 2

    canvas.create_rectangle(
        x0,
        y0,
        x0 + arena_size,
        y0 + arena_size,
        fill="black",
        stipple="gray50",
        outline=""
    )

    canvas.create_text(
        cx,
        cy,
        text=str(countdown_value),
        fill="#FFFFFF",
        font=("Arial", 90, "bold")
    )


def begin_playing():

    global game_state

    game_state = "playing"

    show_pause_button()

    draw_game()

    schedule_move()


# =========================
# CHANGE DIRECTION
# =========================

def change_direction(new_direction):

    opposite = {
        "Up": "Down",
        "Down": "Up",
        "Left": "Right",
        "Right": "Left"
    }

    # Bandingin sama arah terakhir yang udah dibuffer,
    # bukan sama arah yang lagi jalan sekarang, biar
    # belokan cepat berturut-turut tetap kepencet
    if direction_queue:

        reference = direction_queue[-1]

    else:

        reference = direction

    # Jangan boleh langsung balik 180 derajat
    if new_direction == opposite[reference]:

        return

    # Ga usah dibuffer kalau arahnya sama kayak referensi
    if new_direction == reference:

        return

    # Maksimal 2 belokan yang dibuffer
    if len(direction_queue) >= 2:

        return

    direction_queue.append(new_direction)


# =========================
# MOVE SNAKE
# =========================

def move_snake():

    global direction
    global score
    global high_score

    if game_state != "playing":

        return

    if direction_queue:

        direction = direction_queue.pop(0)

    head_x, head_y = snake[0]

    if direction == "Up":

        new_head = (
            head_x,
            head_y - 1
        )

    elif direction == "Down":

        new_head = (
            head_x,
            head_y + 1
        )

    elif direction == "Left":

        new_head = (
            head_x - 1,
            head_y
        )

    else:

        new_head = (
            head_x + 1,
            head_y
        )


    # =========================
    # WALL COLLISION
    # =========================

    if (
        new_head[0] < 0
        or new_head[0] >= GRID_SIZE
        or new_head[1] < 0
        or new_head[1] >= GRID_SIZE
    ):

        game_over()

        return


    # =========================
    # SNAKE COLLISION
    # =========================

    if new_head in snake:

        game_over()

        return


    snake.insert(
        0,
        new_head
    )


    # =========================
    # FOOD
    # =========================

    if new_head in food:

        food.remove(new_head)

        score += 1

        if score > high_score:

            high_score = score

        if len(snake) >= GRID_SIZE * GRID_SIZE:

            game_over(won=True)

            return

        maintain_food()

    else:

        snake.pop()


    draw_game()

    schedule_move()


# =========================
# START GAME
# =========================

def start_game():

    cancel_timer()

    reset_snake()

    initialize_food()

    show_pause_button()

    start_countdown(begin_playing)


# =========================
# RESTART
# =========================

def restart_game():

    start_game()


# =========================
# PAUSE
# =========================

def pause_game():

    global game_state

    if game_state != "playing":

        return

    cancel_timer()

    game_state = "paused"

    draw_pause()


def resume_game():

    if game_state != "paused":

        return

    show_pause_button()

    start_countdown(begin_playing)


# =========================
# MENU SELECTION
# =========================

def update_menu_selection():

    for i, (tag, command) in enumerate(menu_items):

        if i == menu_index:

            canvas.itemconfig(
                tag,
                fill="#00FF00"
            )

        else:

            canvas.itemconfig(
                tag,
                fill="white"
            )


def mouse_select_menu(tag):

    global menu_index

    for i, (item_tag, command) in enumerate(menu_items):

        if item_tag == tag:

            menu_index = i

            break

    update_menu_selection()


# =========================
# MENU BUTTON
# =========================

def create_menu_button(
    text,
    y,
    command,
    tag
):

    menu_items.append(
        (tag, command)
    )

    canvas.create_text(
        canvas.winfo_width() / 2,
        y,
        text=text,
        fill="white",
        font=("Arial", 22, "bold"),
        tags=tag
    )

    canvas.tag_bind(
        tag,
        "<Button-1>",
        lambda event, c=command: c()
    )

    canvas.tag_bind(
        tag,
        "<Enter>",
        lambda event, t=tag:
        mouse_select_menu(t)
    )

    canvas.tag_bind(
        tag,
        "<Leave>",
        lambda event:
        update_menu_selection()
    )


# =========================
# MAIN MENU
# =========================

def main_menu():

    global game_state
    global menu_index
    global menu_items

    cancel_timer()

    game_state = "menu"

    menu_items = []
    menu_index = 0

    hide_pause_button()

    canvas.delete("all")

    width = canvas.winfo_width()
    height = canvas.winfo_height()

    center_x = width / 2
    center_y = height / 2

    canvas.create_text(
        center_x,
        center_y - 150,
        text="SNAKE",
        fill="#00FF00",
        font=("Arial", 50, "bold")
    )

    create_menu_button(
        "PLAY",
        center_y - 40,
        start_game,
        "play_button"
    )

    create_menu_button(
        "CUSTOMIZE",
        center_y + 20,
        customize_menu,
        "customize_button"
    )

    create_menu_button(
        "QUIT",
        center_y + 80,
        window.destroy,
        "quit_button"
    )

    update_menu_selection()


# =========================
# PAUSE MENU
# =========================

def draw_pause():

    canvas.delete("all")

    draw_arena()

    x0, y0, arena_size = get_arena_position()

    center_x = x0 + arena_size / 2
    center_y = y0 + arena_size / 2

    canvas.create_text(
        center_x,
        center_y - 110,
        text="PAUSED",
        fill="white",
        font=("Arial", 34, "bold")
    )

    create_pause_buttons()


def create_pause_buttons():

    global menu_items
    global menu_index

    menu_items = []
    menu_index = 0

    x0, y0, arena_size = get_arena_position()

    center_x = x0 + arena_size / 2
    center_y = y0 + arena_size / 2

    buttons = [
        ("RESUME", center_y - 40, resume_game, "resume_button"),
        ("RESTART", center_y + 10, restart_game, "restart_button"),
        ("MENU", center_y + 60, main_menu, "pause_menu_button"),
        ("QUIT", center_y + 110, window.destroy, "pause_quit_button")
    ]

    for text, y, command, tag in buttons:

        menu_items.append(
            (tag, command)
        )

        canvas.create_text(
            center_x,
            y,
            text=text,
            fill="white",
            font=("Arial", 18, "bold"),
            tags=tag
        )

        canvas.tag_bind(
            tag,
            "<Button-1>",
            lambda event, c=command: c()
        )

        canvas.tag_bind(
            tag,
            "<Enter>",
            lambda event, t=tag:
            mouse_select_menu(t)
        )

        canvas.tag_bind(
            tag,
            "<Leave>",
            lambda event:
            update_menu_selection()
        )

    update_menu_selection()


# =========================
# GAME OVER
# =========================

def game_over(won=False):

    global game_state
    global menu_items
    global menu_index
    global last_result_won

    game_state = "gameover"
    last_result_won = won

    cancel_timer()

    hide_pause_button()

    menu_items = []
    menu_index = 0

    canvas.delete("all")

    x0, y0, arena_size = get_arena_position()

    center_x = x0 + arena_size / 2
    center_y = y0 + arena_size / 2

    if won:

        title_text = "YOU WIN!"
        title_color = "#00FF00"

    else:

        title_text = "GAME OVER"
        title_color = "#FF0000"

    canvas.create_text(
        center_x,
        center_y - 110,
        text=title_text,
        fill=title_color,
        font=("Arial", 34, "bold")
    )

    canvas.create_text(
        center_x,
        center_y - 55,
        text=f"SCORE: {score}",
        fill="white",
        font=("Arial", 20, "bold")
    )

    buttons = [
        ("RESTART", center_y, restart_game, "go_restart"),
        ("MENU", center_y + 50, main_menu, "go_menu"),
        ("QUIT", center_y + 100, window.destroy, "go_quit")
    ]

    for text, y, command, tag in buttons:

        menu_items.append(
            (tag, command)
        )

        canvas.create_text(
            center_x,
            y,
            text=text,
            fill="white",
            font=("Arial", 18, "bold"),
            tags=tag
        )

        canvas.tag_bind(
            tag,
            "<Button-1>",
            lambda event, c=command: c()
        )

        canvas.tag_bind(
            tag,
            "<Enter>",
            lambda event, t=tag:
            mouse_select_menu(t)
        )

        canvas.tag_bind(
            tag,
            "<Leave>",
            lambda event:
            update_menu_selection()
        )

    update_menu_selection()


# =========================
# COLOR PICKERS
# =========================

def choose_head_color():

    global head_color

    color = colorchooser.askcolor(
        title="Choose Head Color",
        initialcolor=head_color
    )

    if color[1]:

        head_color = color[1].upper()

    customize_menu()


def choose_body_start():

    global body_start_color

    color = colorchooser.askcolor(
        title="Choose Body Start Color",
        initialcolor=body_start_color
    )

    if color[1]:

        body_start_color = color[1].upper()

    customize_menu()


def choose_body_end():

    global body_end_color

    color = colorchooser.askcolor(
        title="Choose Body End Color",
        initialcolor=body_end_color
    )

    if color[1]:

        body_end_color = color[1].upper()

    customize_menu()


def reset_colors():

    global head_color
    global body_start_color
    global body_end_color

    head_color = DEFAULT_HEAD
    body_start_color = DEFAULT_BODY_START
    body_end_color = DEFAULT_BODY_END

    customize_menu()


# =========================
# CUSTOMIZE MENU
# =========================

def customize_menu():

    global game_state
    global menu_index
    global menu_items

    cancel_timer()

    game_state = "customize"

    menu_items = []
    menu_index = 0

    hide_pause_button()

    canvas.delete("all")

    width = canvas.winfo_width()
    height = canvas.winfo_height()

    center_x = width / 2
    center_y = height / 2

    canvas.create_text(
        center_x,
        center_y - 230,
        text="CUSTOMIZE",
        fill="white",
        font=("Arial", 36, "bold")
    )


    # =========================
    # PREVIEW
    # =========================

    preview_y = center_y - 145

    preview_colors = [
        body_end_color,
        body_start_color,
        body_start_color,
        head_color
    ]

    start_x = center_x - 90

    for i, color in enumerate(preview_colors):

        canvas.create_rectangle(
            start_x + i * 45,
            preview_y,
            start_x + i * 45 + 40,
            preview_y + 40,
            fill=color,
            outline=""
        )


    create_menu_button(
        "HEAD COLOR",
        center_y - 70,
        choose_head_color,
        "head_color_button"
    )

    create_menu_button(
        "BODY START",
        center_y - 10,
        choose_body_start,
        "body_start_button"
    )

    create_menu_button(
        "BODY END",
        center_y + 50,
        choose_body_end,
        "body_end_button"
    )

    create_menu_button(
        "RESET DEFAULT",
        center_y + 110,
        reset_colors,
        "reset_color_button"
    )

    create_menu_button(
        "BACK",
        center_y + 180,
        main_menu,
        "back_button"
    )

    update_menu_selection()


# =========================
# KEYBOARD
# =========================

def keyboard(event):

    global menu_index

    key = event.keysym.lower()


    # =========================
    # F11
    # =========================

    if key == "f11":

        toggle_fullscreen()

        return


    # =========================
    # PLAYING
    # =========================

    if game_state == "playing":

        if key in ("up", "w"):

            change_direction("Up")

        elif key in ("down", "s"):

            change_direction("Down")

        elif key in ("left", "a"):

            change_direction("Left")

        elif key in ("right", "d"):

            change_direction("Right")

        elif key == "escape":

            pause_game()

        return


    # =========================
    # PAUSED
    # =========================

    if game_state == "paused":

        if not menu_items:

            return

        if key == "escape":

            resume_game()

        elif key in ("up", "w"):

            menu_index = (
                menu_index - 1
            ) % len(menu_items)

            update_menu_selection()

        elif key in ("down", "s"):

            menu_index = (
                menu_index + 1
            ) % len(menu_items)

            update_menu_selection()

        elif key in ("return", "kp_enter"):

            command = menu_items[menu_index][1]

            command()

        return


    # =========================
    # MENU / CUSTOMIZE / GAME OVER
    # =========================

    if game_state in (
        "menu",
        "customize",
        "gameover"
    ):

        if not menu_items:

            return

        if key == "escape":

            if fullscreen:

                toggle_fullscreen()

        elif key in ("up", "w"):

            menu_index = (
                menu_index - 1
            ) % len(menu_items)

            update_menu_selection()

        elif key in ("down", "s"):

            menu_index = (
                menu_index + 1
            ) % len(menu_items)

            update_menu_selection()

        elif key in ("return", "kp_enter"):

            command = menu_items[menu_index][1]

            command()


# =========================
# KEYBOARD BINDING
# =========================

window.bind_all(
    "<KeyPress>",
    keyboard
)


# =========================
# FULLSCREEN
# =========================

def toggle_fullscreen():

    global fullscreen

    fullscreen = not fullscreen

    window.attributes(
        "-fullscreen",
        fullscreen
    )

    window.after(
        100,
        redraw_current_screen
    )


# =========================
# RESIZE
# =========================

def redraw_current_screen():

    if game_state == "playing":

        draw_game()

    elif game_state == "countdown":

        draw_countdown()

    elif game_state == "paused":

        draw_pause()

    elif game_state == "menu":

        main_menu()

    elif game_state == "customize":

        customize_menu()

    elif game_state == "gameover":

        game_over(won=last_result_won)


def schedule_resize_redraw(event=None):

    global resize_after_id

    if resize_after_id is not None:

        try:

            window.after_cancel(
                resize_after_id
            )

        except:

            pass

    resize_after_id = window.after(
        100,
        redraw_after_resize
    )


def redraw_after_resize():

    global resize_after_id

    resize_after_id = None

    redraw_current_screen()


canvas.bind(
    "<Configure>",
    schedule_resize_redraw
)


# =========================
# START PROGRAM
# =========================

window.after(
    100,
    main_menu
)

window.mainloop()