import tkinter as tk
import sys
import os
from PIL import Image, ImageTk
from cairosvg import svg2png
import chess
import chess.svg
import chess.pgn
from util import to_pkl, from_pkl
from tkinter import filedialog


class Trainer:
    def __init__(self):
        self.constants = {"BOARD_CLICK_CONSTANT":".!frame.!frame.!label"}
        self.move_list = list([])
        self.move_stack = list([])
        self.variation_name = ""
        self.is_full_screen = False
        self.variation_idx = 0
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
        sub_menu.add_separator()
        sub_menu.add_command(label='Load PGN', command=self.open_pgn_file)
        sub_menu.add_separator()
        sub_menu.add_command(label='Exit Training Module', command=self.end_it)
        sub_menu.add_separator()
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
        self.root.bind("<Button-1>", self.react_to_click)
        self.root.bind("<Return>", self.refresh)
        self.root.bind("<Escape>", self.end_it)


    def square_set_wrapper(self, square_string):
        '''\
            Convert a string representation of a square on the board into
            a SquareSet to support board highlighting.
        '''
        square_string_index = chess.SQUARE_NAMES.index(square_string)
        return chess.SquareSet.from_square(chess.SQUARES[square_string_index])


    def prepare_training_variation(self, training_variation):
        self.move_list = training_variation['ML']
        self.variation_name = training_variation['name']
        self.update_variation_name()
        self.V.reset()
        for move in self.move_list:
            self.V.push(self.V.parse_san(move))
        self.move_stack = list(self.V.move_stack)


    def update_variation_progress(self):
        move_string = self.move_list[self.variation_idx-1]
        if (((self.variation_idx - 1) % 2) == 0):
            self.variation_progress += "{}. {} ".format(self.K.fullmove_number, move_string)
        else:
            self.variation_progress += "{}\n".format(move_string)
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
        '''\
            Create and display an updated representation of the game state.
        '''
        self.save_board_image(self.K, square_string)
        self.board_to_show = self.prepare_image('new_board')
        self.board_label.configure(image=self.board_to_show)
        self.board_label.image = self.board_to_show


    def save_board_image(self, board_obj, square_string=None):
        '''\
            Create an updated representation of the game state, with or without highlighting.
        '''
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
        return self.move_stack[self.variation_idx]

    @property
    def variation_is_complete(self):
        return self.variation_idx == len(self.move_stack)


    def update_training_progress(self):
        self.variation_idx += 1
        if self.variation_is_complete:
            self.update_warning('Variation completed!', '#00ff00')
        self.update_variation_progress()


    def refresh(self, event='<Return>'):
        self.start_square = ''
        self.end_square = ''
        self.have_clicked = False
        self.K.reset()
        self.variation_idx = 0
        self.update_board_image()
        self.variation_progress = '\n'
        self.update_progress()
        self.update_variation_name()
        self.update_warning('\n')


    def end_it(self, event="<Escape>"):
        self.root.overrideredirect(0)
        self.root.geometry("100x100")
        self.root.destroy()


    def remove_extension(self, filename, extension):
        if filename.endswith(extension):
            n_chars_to_remove = len(extension)
            filename = filename[:-n_chars_to_remove]
        return filename


    def solve_filename(self, filename):
        # NOTE #
        # This approach will fail if filenames contain forward slashes.
        if ("/" in filename):
            reversed_filename = filename[::-1]
            reversed_filename_slash_index = reversed_filename.index('/')
            reversed_filename_particle = reversed_filename[:reversed_filename_slash_index]
            filename = reversed_filename_particle[::-1]
        return filename


    def solve_pgn_filename(self, filename):
        return self.remove_extension(self.solve_filename(filename), ".pgn")


    def load_pgn(self, filename):
        try:
            with open(filename) as pgn:
                pgn_game = chess.pgn.read_game(pgn)
                pgn_board = pgn_game.board()
                pgn_mainline = list(pgn_game.main_line())

                variation_moves = []
                for move in pgn_mainline:
                    variation_moves.append(pgn_board.san(move))
                    pgn_board.push(move)

                variation = {'name':self.solve_pgn_filename(filename), 'ML':variation_moves}

        except:
            variation = None

        finally:
            return variation


    def open_pgn_file(self):
        filename = filedialog.askopenfilename(initialdir='./PGN/',
                                              title='Select PGN training variation',
                                              filetypes=(("PGN Files", "*.pgn"),))
        # Case: Didn't select the 'Cancel' option in the filedialog.
        if ((type(filename) == str) and (filename != "")):
            variation = self.load_pgn(filename)
            # Case: load_pgn succeeded in loading and converting the PGN into the variation format.
            if (variation is not None):
                self.prepare_training_variation(variation)
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


    def react_to_click(self, event):
        # Case # Variation isn't complete yet.
        if not(self.variation_is_complete):
            # Case # Click occurred over the subset of the GUI containing the board.
            if (event.widget._w == self.constants['BOARD_CLICK_CONSTANT']):
                # Case # start_square is specified.
                if self.have_clicked:
                    self.have_clicked = False
                    self.end_square = self.solve_square(event.x, event.y)
                    uci_move = self.uci_move_from_string(self.start_square, self.end_square)
                    legals = list(self.K.legal_moves)
                    # Case: end_square choice corresponds to is an invalid move.
                    #       an invalid move. echo the warning and clear the board of any highlights.
                    if (uci_move not in legals):
                        self.update_warning('Not a legal move!')
                        self.update_board_image()

                    # Case: end_square choice corresponds to a legal move, but not the correct one.
                    #       echo a hint and clear the board of any highlights.
                    elif (uci_move != self.which_move_in_variation):
                        self.update_warning('Incorrect! Hint: {}'.format(self.K.san(self.which_move_in_variation)))
                        self.update_board_image()

                    # Case: end_square choice corresponds to the correct move.
                    else:
                        self.update_warning('Correct!', '#00ff00')
                        self.K.push(uci_move)
                        self.update_board_image()
                        self.update_training_progress()

                # Case # start_square is unspecified.
                else:
                    self.have_clicked = True
                    self.start_square = self.solve_square(event.x, event.y)
                    self.update_board_image(square_string=self.start_square)


    def rank_coordinate(self, y):
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


    def file_coordinate(self, x):
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
        return self.file_coordinate(x) + self.rank_coordinate(y)


    def toggle_fullscreen(self, event):
        if self.is_full_screen:
            self.is_full_screen = False
            self.root.attributes('-fullscreen', False)
        else:
            self.is_full_screen = True
            self.root.attributes('-fullscreen', True)


    def create_default_pgn(self):
        '''\
            Ensure the correct default PGN exists in the correct subdirectory.
        '''
        self.create_pgn_subdirectory()
        with open("./PGN/Scholar's Mate.pgn", "w") as default_pgn_file:
            default_pgn_file.write("1. e4 e5 2. Bc4 Bc5 3. Qf3 Nc6 4. Qxf7#")
            default_pgn_file.close()


    def create_pgn_subdirectory(self):
        '''\
            Ensure the PGN subdirectory exists.
        '''
        if not(os.path.exists("PGN")):
            os.mkdir("PGN")


    def verify_preconditions(self):
        '''\
            Ensure assumptions are made safely.
        '''
        self.create_default_pgn()


    def start(self):
        self.verify_preconditions()
        self.prepare_training_variation(self.load_pgn("./PGN/Scholar's Mate.pgn"))
        self.update_variation_name()
        self.root.mainloop()


TRAINER = Trainer()
TRAINER.start()
