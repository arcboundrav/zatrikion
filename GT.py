import tkinter as tk
import sys
from PIL import Image, ImageTk
from cairosvg import svg2png
import chess
import chess.svg
from z_help import to_pkl, from_pkl
from tkinter import filedialog

K = chess.Board()
V = chess.Board()
move_list = []
move_stack = []

def load_vari(fn, fp='./pkl/training/'):
    return from_pkl(fn, fp)

def save_vari(vari_to_save, fn, fp='./pkl/training/'):
    to_pkl(vari_to_save, fn, fp)

def prep_training_vari(fn='default_training_variation'):
    global move_list, move_stack, variation_name
    training_vari = load_vari(fn)
    move_list = training_vari['ML']
    variation_name = training_vari['name']
    for move in move_list:
        V.push(V.parse_san(move))
    move_stack = V.move_stack[:]

is_full_screen = False
vari_i = 0
have_clicked = False
start_square = ''
end_square = ''


def update_vari_progress():
    global variation_progress, vari_i, move_list
    progress = '{}. {} {}'.format(K.fullmove_number-1, move_list[vari_i-2], move_list[vari_i-1])
    progress = pad_me(progress)
    variation_progress += progress
    update_progress(variation_progress)


def update_board_img():
    save_board_image(K)
    board_to_show = prep_img('new_board')
    label.configure(image=board_to_show)
    label.image = board_to_show


def save_new_base_board_image(event):
    board_image = chess.svg.board(board=K, coordinates=False, size=640)
    svg2png(board_image, write_to=("init_board.png"))


def save_board_image(board_obj):
    board_image = chess.svg.board(board=board_obj, coordinates=False, size=640)
    svg2png(board_image, write_to=("new_board.png"))


def prep_img(img_fn, img_fx='.png'):
    return ImageTk.PhotoImage(Image.open(img_fn+img_fx))


def which_move_in_vari():
    global move_stack, vari_i
    return move_stack[vari_i]


def update_training_progress():
    global move_stack, vari_i
    vari_i += 1
    if vari_i == len(move_stack):
        #print('Variation completed!')
        update_warning('Variation completed!', '#00ff00')
    else:
        K.push(move_stack[vari_i])
        update_board_img()
        vari_i += 1
        update_vari_progress()
        if vari_i == len(move_stack):
            update_warning('Variation completed!', '#00ff00')


def refresh(event='<Return>'):
    global vari_i, variation_progress, have_clicked, start_square, end_square
    start_square = ''
    end_square = ''
    have_clicked = False
    K.reset()
    vari_i = 0
    update_board_img()
    variation_progress = '\n'
    update_progress(variation_progress)
    update_variation_name(variation_name)
    update_warning('\n')


def end_it(event="<Escape>"):
    root.overrideredirect(0)
    root.geometry("100x100")
    root.destroy()


def pad_me(base, ref=15):
    pad_n = ref - len(base)
    pad = ' ' * pad_n
    return base + pad + '\n'


root = tk.Tk()
root.title("Zatrikion")
#root.resizable(False, False)
#w, h = root.winfo_screenwidth(), root.winfo_screenheight()
#root.overrideredirect(1)
#root.geometry("%dx%d+0+0" % (w, h))

def parse_fn(fn):
    rev_fn = fn[::-1]
    rev_fn_slash_i = rev_fn.index('/')
    rev_fn_particle = rev_fn[2:rev_fn_slash_i]
    true_fn = rev_fn_particle[::-1]
    print(true_fn)
    return true_fn


def open_file():
    filename = filedialog.askopenfilename(initialdir='./pkl/training', title= 'Select training variation')
    #print(filename)
    filename = parse_fn(filename)
    V.reset()
    prep_training_vari(filename)
    refresh()


menu = tk.Menu(root, tearoff=0)
root.configure(menu=menu)
subMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='Options', menu=subMenu)
subMenu.add_separator()
subMenu.add_command(label='Refresh Current Variation', command=refresh)
subMenu.add_command(label='Load Variation', command=open_file)
subMenu.add_separator()
subMenu.add_command(label='Exit Training Module', command=end_it)

base = tk.Frame(root, bg='#393e39')
base.pack()

board_to_show = prep_img('init_board')

board_frame = tk.Frame(base)
data_frame = tk.Frame(base, bg='#000000', width=100)

board_frame.grid(row=0, column=0, sticky=tk.W)
data_frame.grid(row=0, column=1, sticky=[tk.W, tk.N])

label = tk.Label(board_frame, image=board_to_show, bg='#ffffff', border=2, relief=tk.SUNKEN)
label.grid(row=0)

variation_name = '\n'
label4 = tk.Label(data_frame, text=variation_name, font=('Cambria', 12, 'bold'), width=50, fg='#ffff00', bg='#000000')
label4.grid(row=0, sticky=[tk.S])

variation_progress = '\n'
label2 = tk.Label(data_frame, text=variation_progress, font=('Cambria', 12), width=50, justify=tk.LEFT, fg="#dae5d9", bg='#000000', border=2, relief=tk.SUNKEN)
label2.grid(row=1, sticky=[tk.W, tk.N])


warning = '\n'
label3 = tk.Label(data_frame, text=warning, font=('Cambria', 12), justify=tk.RIGHT, fg='#ff0000', bg='#000000')
label3.grid(row=2, sticky=[tk.S])



def update_warning(new_warning, color='#ff0000'):
    global warning
    warning = new_warning
    label3.configure(text = warning, fg=color)
    label3.fg = color
    label3.text = warning


def update_progress(new_progress):
    label2.configure(text = new_progress)
    label2.text = new_progress


def update_variation_name(vari_name):
    label4.configure(text = vari_name)
    label4.text = vari_name


def uci_move_from_str(start_sq_str, end_sq_str):
    return chess.Move.from_uci(start_sq_str + end_sq_str)


def where_am_i(event):
    global have_clicked, start_square, end_square
    if have_clicked:
        have_clicked = False
        end_square = solve_square(event.x, event.y)
        #print('End Square: {}'.format(end_square))
        uci_move = uci_move_from_str(start_square, end_square)
        legals = list(K.legal_moves)
        if (uci_move not in legals):
            #print('Not a legal move!')
            update_warning('Not a legal move!')
        elif (uci_move != which_move_in_vari()):
            #print('Incorrect!')
            update_warning('Incorrect! Hint: {}'.format(K.san(which_move_in_vari())))
            #print(K.san(which_move_in_vari()))
        else:
            update_warning('Correct!', '#00ff00')
            K.push(uci_move)
            update_board_img()
            update_training_progress()
    else:
        have_clicked = True
        start_square = solve_square(event.x, event.y)
        #print('Start Square: {}'.format(start_square))


def rank_coord(y):
    if y > 560:
        return '1'
    elif y > 480:
        return '2'
    elif y > 400:
        return '3'
    elif y > 320:
        return '4'
    elif y > 240:
        return '5'
    elif y > 160:
        return '6'
    elif y > 80:
        return '7'
    else:
        return '8'


def file_coord(x):
    if x > 560:
        return 'h'
    elif x > 480:
        return 'g'
    elif x > 400:
        return 'f'
    elif x > 320:
        return 'e'
    elif x > 240:
        return 'd'
    elif x > 160:
        return 'c'
    elif x > 80:
        return 'b'
    else:
        return 'a'


def solve_square(x, y):
    x_str = file_coord(x)
    y_str = rank_coord(y)
    sq_str = x_str + y_str
    #print(sq_str)
    return sq_str


def f(event):
    print(event.x, event.y)


def toggle_fullscreen(event):
    global is_full_screen
    if is_full_screen:
        is_full_screen = False
        root.attributes('-fullscreen', False)
    else:
        is_full_screen = True
        root.attributes('-fullscreen', True)

#root.bind("<Motion>", f)
root.focus_set()
root.bind("a", toggle_fullscreen)
root.bind("<Button-1>", where_am_i)
root.bind("<Return>", refresh)
root.bind("<Escape>", end_it)


#root.mainloop()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        prep_training_vari(sys.argv[1])
    else:
        prep_training_vari()
    update_variation_name(variation_name)
    root.mainloop()
