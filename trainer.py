import tkinter as tk
import sys
from PIL import Image, ImageTk
from cairosvg import svg2png
import chess
import chess.svg
from util import to_pkl, from_pkl
from tkinter import filedialog


class Trainer:
    def __init__(self):
        self.move_list = list([])
        self.move_stack = list([])
        self.variation_name = ""
        self.is_full_screen = False
        self.vari_i = 0
        self.variation_progress = ""
        self.have_clicked = False
        self.start_square = ""
        self.end_square = ""
        self.K = chess.Board()
        self.V = chess.Board()

        self.root = self.create_root()
        self.menu = self.create_menu()
        self.root.configure(menu=self.menu)

        self.base = self.create_base()

        self.save_new_base_board_image()
        self.board_to_show = self.prepare_image('init_board')

        self.board_frame = self.create_board_frame()
        self.data_frame = self.create_data_frame()

        self.board_label = self.create_board_label()

        self.variation_name = '\n'
        self.label4 = tk.Label(self.data_frame,
                               text=self.variation_name,
                               font=('Cambria', 12, 'bold'), width=50, fg='#ffff00', bg='#000000')
        self.label4.grid(row=0, sticky=[tk.S])

        self.variation_progress = '\n'
        self.label2 = tk.Label(self.data_frame,
                               text=self.variation_progress,
                               font=('Cambria', 12), width=50, justify=tk.LEFT, fg="#dae5d9", bg='#000000', border=2, relief=tk.SUNKEN)
        self.label2.grid(row=1, sticky=[tk.W, tk.N])

        self.warning = '\n'
        self.label3 = tk.Label(self.data_frame,
                               text=self.warning,
                               font=('Cambria', 12), justify=tk.RIGHT, fg='#ff0000', bg='#000000')
        self.label3.grid(row=2, sticky=[tk.S])

        self.assign_root_bindings()


    def create_root(self):
        root = tk.Tk()
        root.title("Zatrikion")
        return root


    def create_menu(self):
        menu = tk.Menu(self.root, tearoff=0)
        sub_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Options", menu=sub_menu)
        sub_menu.add_separator()
        sub_menu.add_command(label='Refresh Current Variation', command=self.refresh)
        sub_menu.add_command(label='Load Variation', command=self.open_file)
        sub_menu.add_separator()
        sub_menu.add_command(label='Exit Training Module', command=self.end_it)
        return menu


    def create_base(self):
        base = tk.Frame(self.root, bg='#393e39')
        base.pack()
        return base


    def create_board_frame(self):
        frame = tk.Frame(self.base)
        frame.grid(row=0, column=0, sticky=tk.W)
        return frame


    def create_data_frame(self):
        frame = tk.Frame(self.base, bg='#000000', width=100)
        frame.grid(row=0, column=1, sticky=[tk.W, tk.N])
        return frame


    def create_board_label(self):
        label = tk.Label(self.board_frame,
                         image=self.board_to_show, bg='#ffffff', border=2, relief=tk.SUNKEN)
        label.grid(row=0)
        return label


    def assign_root_bindings(self):
        self.root.focus_set()
        self.root.bind("a", self.toggle_fullscreen)
        self.root.bind("<Button-1>", self.where_am_i)
        self.root.bind("<Return>", self.refresh)
        self.root.bind("<Escape>", self.end_it)


    def square_set_wrapper(self, square_string):
        square_string_index = chess.SQUARE_NAMES.index(square_string)
        return chess.SquareSet.from_square(chess.SQUARES[square_string_index])


    def pad_me(self, string, ref=15):
        pad_n = ref - len(string)
        pad = ' ' * pad_n
        return "".join([string, pad, '\n'])


    def load_variation(self, fn, fp="./pkl/training/"):
        return from_pkl(fn, fp)


    def save_variation(self, variation_to_save, fn, fp="./pkl/training/"):
        to_pkl(variation_to_save, fn, fp)


    def prepare_training_variation(self, fn="default_training_variation"):
        training_variation = self.load_variation(fn)
        self.move_list = training_variation['ML']
        self.variation_name = training_variation['name']
        self.update_variation_name()
        for move in self.move_list:
            self.V.push(self.V.parse_san(move))
        self.move_stack = list(self.V.move_stack)


    def update_variation_progress(self):
        self.variation_progress += self.pad_me('{}. {} {}'.format(self.K.fullmove_number-1,
                                                                  self.move_list[self.vari_i-2],
                                                                  self.move_list[self.vari_i-1]))
        self.update_progress()


    def save_new_base_board_image(self):
        '''\
            Create the correct initial position image.
        '''
        board_image = chess.svg.board(board=self.K,
                                      coordinates=False,
                                      size=640)
        svg2png(board_image, write_to=("init_board.png"))


    def update_board_image(self, square_string=None):
        self.save_board_image(self.K, square_string)
        self.board_to_show = self.prepare_image('new_board')
        self.board_label.configure(image=self.board_to_show)
        self.board_label.image = self.board_to_show


    def save_board_image(self, board_obj, square_string=None):
        if (square_string is None):
            board_image = chess.svg.board(board=board_obj, coordinates=False, size=640)
        else:
            board_image = chess.svg.board(board=board_obj,
                                          squares=self.square_set_wrapper(square_string),
                                          square_flag="I",
                                          coordinates=False,
                                          size=640)
        svg2png(board_image, write_to=("new_board.png"))


    def prepare_image(self, img_fn, img_fx='.png'):
        return ImageTk.PhotoImage(Image.open(img_fn+img_fx))


    @property
    def which_move_in_variation(self):
        return self.move_stack[self.vari_i]


    def update_training_progress(self):
        self.vari_i += 1
        if (self.vari_i == len(self.move_stack)):
            self.update_warning('Variation completed!', '#00ff00')
        else:
            self.K.push(self.move_stack[self.vari_i])
            self.update_board_image()
            self.vari_i += 1
            self.update_variation_progress()
            if (self.vari_i == len(self.move_stack)):
                self.update_warning('Variation completed!', '#00ff00')


    def refresh(self, event='<Return>'):
        self.start_square = ''
        self.end_square = ''
        self.have_clicked = False
        self.K.reset()
        self.vari_i = 0
        self.update_board_image()
        self.variation_progress = '\n'
        self.update_progress()
        self.update_variation_name()
        self.update_warning('\n')


    def end_it(self, event="<Escape>"):
        self.root.overrideredirect(0)
        self.root.geometry("100x100")
        self.root.destroy()


    def parse_fn(self, fn):
        rev_fn = fn[::-1]
        rev_fn_slash_i = rev_fn.index('/')
        rev_fn_particle = rev_fn[2:rev_fn_slash_i]
        true_fn = rev_fn_particle[::-1]
        return true_fn


    def open_file(self):
        filename = filedialog.askopenfilename(initialdir='./pkl/training', title='Select training variation')
        #print("DEBUG | filename <{}>: {} [{}]".format(type(filename), filename, len(filename)))
        # Case: Didn't select the 'Cancel' option in the filedialog.
        if ((type(filename) == str) and (filename != "")):
            filename = self.parse_fn(filename)
            self.V.reset()
            self.prepare_training_variation(filename)
            self.refresh()


    def update_warning(self, new_warning, color='#ff0000'):
        self.warning = new_warning
        self.label3.configure(text=self.warning, fg=color)
        self.label3.fg = color
        self.label3.text = self.warning


    def update_progress(self):
        self.label2.configure(text=self.variation_progress)
        self.label2.text = self.variation_progress


    def update_variation_name(self):
        self.label4.configure(text=self.variation_name)
        self.label4.text = self.variation_name


    def uci_move_from_string(self, start_square_string, end_square_string):
        return chess.Move.from_uci(start_square_string + end_square_string)


    def where_am_i(self, event):
        #print("DEBUG | event.x: {} event.y: {}".format(event.x, event.y))
        print("DEBUG | {}".format(event.__dict__['widget'].__dict__['_w']))
        # NOTE #
        # event.__dict__['widget'].__dict__['_w'] == '.!frame.!frame.!label'
        # only when a click occurs on the board.
        if self.have_clicked:
            self.have_clicked = False
            self.end_square = self.solve_square(event.x, event.y)
            uci_move = self.uci_move_from_string(self.start_square, self.end_square)
            legals = list(self.K.legal_moves)
            # Case: start_square is specified. end_square choice corresponds to
            #       an invalid move. echo the warning and clear the board of any highlights.
            if (uci_move not in legals):
                self.update_warning('Not a legal move!')
                self.update_board_image()

            # Case: start_square is specified. end_square choice corresponds to
            #       a legal move, but not the correct move. echo a hint and clear
            #       the board of any highlights.
            elif (uci_move != self.which_move_in_variation):
                self.update_warning('Incorrect! Hint: {}'.format(self.K.san(self.which_move_in_variation)))
                self.update_board_image()

            # Case: start_square is specified. end_square choice corresponds to a legal move:
            #       the correct move.
            else:
                self.update_warning('Correct!', '#00ff00')
                self.K.push(uci_move)
                self.update_board_image()
                self.update_training_progress()
        else:
            self.have_clicked = True
            self.start_square = self.solve_square(event.x, event.y)
            self.update_board_image(square_string=self.start_square)


    def rank_coord(self, y):
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


    def file_coord(self, x):
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


    def solve_square(self, x, y):
        x_str = self.file_coord(x)
        y_str = self.rank_coord(y)
        return x_str + y_str


    def toggle_fullscreen(self, event):
        if self.is_full_screen:
            self.is_full_screen = False
            self.root.attributes('-fullscreen', False)
        else:
            self.is_full_screen = True
            self.root.attributes('-fullscreen', True)


    def start(self):
        self.prepare_training_variation()
        self.update_variation_name()
        self.root.mainloop()


TRAINER = Trainer()
TRAINER.start()
