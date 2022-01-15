import sys
from tkinter import Button, Canvas, E, Frame, HORIZONTAL, IntVar, N, Scale, StringVar, SW, Tk
from tkinter.ttk import Combobox
from tkinter.font import Font

from wordgame.game import Game, InvalidGuess, State, LetterState
from wordgame.solver import Solver
from wordgame.words import WORD_SETS


class Colors:
    DEFAULT = "#ffffff"
    SELECTED = "#aaaaff"
    CORRECT = "#88dd88"
    MISPLACED = "#ffff88"
    WRONG = "#ee8888"
    GREYED = "#cccccc"


KEY_COLORS = {
    LetterState.EXACT: Colors.CORRECT,
    LetterState.NONE: Colors.GREYED,
    LetterState.SOME: Colors.MISPLACED,
    LetterState.UNKNOWN: Colors.DEFAULT,
}

XSCALE = 1.75
YSCALE = 1.75

LETTERS_BY_FREQUENCY = [
    "e",
    "a",
    "r",
    "o",
    "t",
    "l",
    "i",
    "s",
    "n",
    "c",
    "u",
    "y",
    "d",
    "h",
    "p",
    "m",
    "g",
    "b",
    "f",
    "k",
    "w",
    "v",
    "z",
    "x",
    "q",
    "j",
]


def sx(x):
    return int(XSCALE * x)


def sy(y):
    return int(YSCALE * y)


class GameWidget:
    # Letterbox geometry
    width = sx(30)
    height = sy(30)
    x_pad = sx(10)
    y_pad = sy(10)
    y0 = sy(10)
    x0 = sx(10)

    # Keyboard geometry
    keys_width = sx(20)
    keys_height = sy(20)
    keys_x_pad = sx(4)
    keys_y_pad = sy(4)
    keys_x0 = sx(5)
    keys_y0 = sy(5)

    def __init__(self, root):
        self.root = root
        self.n_tries_var = IntVar(root, 6)
        self.word_set_var = StringVar(root, "wordle")
        self.game = self.create_game()

        self.guesses_canvas = None
        self.keys_canvas = None

        self.reset_guess()
        self.current_cell = 0
        self.button_ok = None
        self.invalid_guess = False
        self.input_cells = {}

        self.letter_font = Font(size=18)
        self.keyboard_font = Font(size=10)

    def create_game(self):
        return Game(tries=self.n_tries_var.get(), wordset=WORD_SETS[self.word_set_var.get()])

    @property
    def letter_count(self):
        return self.game.wordset.letter_count

    def reset_guess(self):
        self.current_guess = [" "] * self.letter_count
        self.current_cell = 0

    def _compute_canvas_size(self, rows, cols):
        cv_height = 2 * self.y0 + (self.height + self.y_pad) * rows
        cv_width = 2 * self.x0 + (self.width + self.x_pad) * cols
        return cv_height, cv_width

    def reset_canvas(self):
        if self.guesses_canvas:
            self.guesses_canvas.destroy()
            self.guesses_canvas = None
        h, w = self._compute_canvas_size(self.game.tries, self.letter_count + 1)
        self.guesses_canvas = Canvas(self.guesses_frame, width=w, height=h)
        self.guesses_canvas.pack()
        if self.keys_canvas:
            self.keys_canvas.destroy()
            self.keys_canvas = None
        h, w = self._compute_canvas_size(1, self.letter_count + 1)
        self.keys_canvas = Canvas(self.keys_frame, width=w + sx(100), height=h + sx(20))
        self.keys_canvas.pack(anchor=SW)

    def get_coords(self, row, col):
        """Get x, y coords for box at position row, column"""
        x = self.x0 + (self.width + self.x_pad) * col
        y = self.y0 + (self.height + self.y_pad) * row
        return x, y

    def get_keys_coords(self, row, col):
        """Get x, y coords for keyboard indicator at position row, column"""
        x = self.keys_x0 + (self.keys_width + self.keys_x_pad) * col
        y = self.keys_y0 + (self.keys_height + self.keys_y_pad) * row
        return x, y

    def draw_letterbox(self, row, col, letter=" ", color=Colors.DEFAULT):
        """draw a letter box at given position."""
        x0, y0 = self.get_coords(row, col)
        x1 = x0 + self.width
        y1 = y0 + self.height

        box = self.guesses_canvas.create_rectangle(x0, y0, x1, y1, fill=color)
        self.guesses_canvas.create_text(
            (x0 + x1) / 2, (y0 + y1) / 2, text=letter, font=self.letter_font
        )
        return box

    def draw_key(self, row, col, letter, color):
        x0, y0 = self.get_keys_coords(row, col)
        x1 = x0 + self.keys_width
        y1 = y0 + self.keys_height
        self.keys_canvas.create_rectangle(x0, y0, x1, y1, fill=color)
        self.keys_canvas.create_text(
            (x0 + x1) / 2, (y0 + y1) / 2, text=letter, font=self.keyboard_font
        )

    def draw_keys(self):
        states = self.game.letter_states()
        for (i, letter) in enumerate(LETTERS_BY_FREQUENCY):
            row = i // 13
            col = i % 13
            color = KEY_COLORS[states[letter]]
            self.draw_key(row, col, letter, color)

    def submit_guess(self):
        try:
            self.game.guess("".join(self.current_guess))
        except InvalidGuess:
            self.invalid_guess = True
        self.reset_guess()

    def draw_input_cells(self):
        if self.input_cells:
            for entry in self.input_cells.keys():
                self.guesses_canvas.delete(entry)
        self.input_cells = {}
        i = len(self.game.guesses)
        unselected = Colors.WRONG if self.invalid_guess else Colors.DEFAULT
        for j in range(self.letter_count):
            color = Colors.SELECTED if j == self.current_cell else unselected
            letter = self.current_guess[j]
            id = self.draw_letterbox(i, j, color=color, letter=letter)
            self.guesses_canvas.tag_bind(id, "<ButtonPress-1>", self.on_entry_click)
            self.input_cells[id] = j

    def draw_previous_guess(self, i):
        guess, response = self.game.guesses[i]
        for j, (letter, state) in enumerate(zip(guess, response)):
            self.draw_letterbox(i, j, letter=letter, color=KEY_COLORS[state])

    def draw_game(self):
        self.guesses_canvas.delete("all")

        for i in range(len(self.game.guesses)):
            self.draw_previous_guess(i)

        # draw current guess
        i = len(self.game.guesses)

        if i < self.game.tries:
            self.draw_input_cells()
            self.invalid_guess = False

        # draw empty guesses remaining
        for i in range(len(self.game.guesses), self.game.tries):
            for j in range(self.letter_count):
                self.draw_letterbox(i, j)

        self.draw_keys()

    def on_entry_click(self, event):
        self.current_cell = self.input_cells[event.widget.find_closest(event.x, event.y)[0]]
        self.draw_input_cells()

    def input_char(self, char):
        if self.game.state != State.OPEN:
            return
        if self.current_cell < self.letter_count:
            self.current_guess[self.current_cell] = char

    def input_clear(self):
        if self.game.state != State.OPEN:
            return
        self.input_char(" ")

    def input_advance(self):
        if self.game.state != State.OPEN:
            return
        if self.current_cell < self.letter_count:
            self.current_cell += 1

    def input_back(self):
        if self.game.state != State.OPEN:
            return
        if self.current_cell > 0:
            self.current_cell -= 1

    def undo(self):
        if self.game.guesses:
            self.game.guesses.pop()

    def on_keypress(self, event):
        if event.keysym == "BackSpace":
            self.input_back()
            self.input_clear()
            self.draw_game()
        elif event.keysym == "Return":
            self.submit_guess()
            self.draw_game()
        elif event.keysym == "Left":
            self.input_back()
            self.draw_game()
        elif event.keysym == "Right":
            self.input_advance()
            self.draw_game()
        elif event.char and ord(event.char) in range(ord("a"), ord("z") + 1):
            self.input_char(event.char)
            self.input_advance()
            self.draw_game()

    def button_new_game(self):
        self.game = self.create_game()
        self.reset_guess()
        self.reset_canvas()
        self.draw_game()

    def button_restart(self):
        self.game.restart()
        self.reset_guess()
        self.draw_game()

    def button_undo(self):
        self.undo()
        self.draw_game()

    def button_solve(self):
        if self.button_ok:
            self.button_ok.destroy()
        solver = Solver(self.game)
        solver.guess()
        self.draw_game()

    def destroy(self):
        self.guesses_frame.destroy()
        self.keys_frame.destroy()
        self.title_frame.destroy()
        self.menu_frame.destroy()
        self.root.unbind("<KeyPress>", self.on_keypress_callback_id)

    def render(self):
        root = self.root
        self.on_keypress_callback_id = root.bind("<KeyPress>", self.on_keypress)

        self.guesses_frame = Frame(root)
        self.keys_frame = Frame(root)
        self.reset_canvas()
        self.draw_game()

        # Menu
        button_row = 0

        def menu_grid(widget):
            nonlocal button_row
            widget.grid(row=button_row, column=0, sticky=N + E)
            button_row += 1

        def menu_button(text, command):
            button = Button(
                self.menu_frame, text=text, width=button_width, font=button_font, command=command
            )
            menu_grid(button)

        self.menu_frame = Frame(root)
        button_font = Font(size=12)
        button_width = sx(12)

        select_wordset = Combobox(
            self.menu_frame,
            textvariable=self.word_set_var,
            values=list(WORD_SETS.keys()),
            font=button_font,
            width=button_width,
        )
        menu_grid(select_wordset)

        select_tries = Scale(
            self.menu_frame,
            variable=self.n_tries_var,
            length=button_width * 10,
            orient=HORIZONTAL,
            from_=1,
            to=10,
        )
        menu_grid(select_tries)

        menu_button("NEW GAME", self.button_new_game)
        menu_button("RESTART", self.button_restart)
        menu_button("UNDO", self.button_undo)
        menu_button("SOLVER", self.button_solve)
        menu_button("QUIT", lambda: sys.exit(0))

        # Title
        self.title_frame = Frame(root)
        self.title_canvas = Canvas(self.title_frame, width=sx(400), height=sy(50))
        self.title_canvas.create_text(
            sx(200), sy(30), text="Untitled Word Game", font=Font(size=30)
        )
        self.title_canvas.pack()

        # Layout
        self.title_frame.grid(row=0, column=0, columnspan=2)
        self.menu_frame.grid(row=1, column=0, sticky=N + E, pady=sy(20), padx=sx(20))
        self.guesses_frame.grid(row=1, column=1, rowspan=2)
        self.keys_frame.grid(row=3, column=0, columnspan=2)


def main():
    root = Tk()
    root.title("Untitled Word Game")
    game_widget = GameWidget(root)
    game_widget.render()
    root.mainloop()


if __name__ == "__main__":
    main()
