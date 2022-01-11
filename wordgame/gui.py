import argparse
import sys
from tkinter import Tk, Canvas, Frame, Button, N, E
from tkinter.font import Font

from wordgame.game import Game, InvalidGuess, State, LetterState
from wordgame.solver import Solver, Treshold


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

XSCALE = 2
YSCALE = 2


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
    kb_width = sx(20)
    kb_height = sy(20)
    kb_x_pad = sx(5)
    kb_y_pad = sy(5)
    kb_x0 = sx(5)
    kb_y0 = sy(5)

    def __init__(self, game, frame, kb_frame):
        self.game = game
        self.frame = frame
        self.kb_frame = kb_frame

        self.canvas = None
        self.kb_canvas = None
        self.reset_canvas()

        self.reset_guess()
        self.current_cell = 0
        self.show_solution = False
        self.button_ok = None
        self.invalid_guess = False
        self.input_cells = {}

        self.letter_font = Font(size=18)
        self.keyboard_font = Font(size=10)

    def reset_guess(self):
        self.current_guess = [" "] * 5
        self.current_cell = 0

    def _compute_canvas_size(self, rows, cols):
        cv_height = 2 * self.y0 + (self.height + self.y_pad) * rows
        cv_width = 2 * self.x0 + (self.width + self.x_pad) * cols
        return cv_height, cv_width

    def set_game(self, game):
        self.game = game
        self.reset_guess()
        self.show_solution = False

    def reset_canvas(self):
        if self.canvas:
            self.canvas.destroy()
            self.canvas = None
        h, w = self._compute_canvas_size(self.game.tries + 1, 6)
        self.canvas = Canvas(self.frame, width=w, height=h)
        self.canvas.pack()
        if self.kb_canvas:
            self.kb_canvas.destroy()
            self.kb_canvas = None
        h, w = self._compute_canvas_size(1, 6)
        self.kb_canvas = Canvas(
            self.kb_frame, width=w + sx(100), height=h + sx(20)
        )
        self.kb_canvas.pack()

    def get_coords(self, row, col):
        """Get x, y coords for box at position row, column"""
        x = self.x0 + (self.width + self.x_pad) * col
        y = self.y0 + (self.height + self.y_pad) * row
        return x, y

    def get_kb_coords(self, row, col):
        """Get x, y coords for keyboard indicator at position row, column"""
        x = self.kb_x0 + (self.kb_width + self.kb_x_pad) * col
        y = self.kb_y0 + (self.kb_height + self.kb_y_pad) * row
        return x, y

    def draw_letterbox(self, row, col, letter=" ", color=Colors.DEFAULT):
        """draw a letter box at given position."""
        x0, y0 = self.get_coords(row, col)
        x1 = x0 + self.width
        y1 = y0 + self.height

        box = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
        self.canvas.create_text(
            (x0 + x1) / 2, (y0 + y1) / 2, text=letter, font=self.letter_font
        )
        return box

    def draw_keyboard_key(self, row, col, letter, color):
        x0, y0 = self.get_kb_coords(row, col)
        x1 = x0 + self.kb_width
        y1 = y0 + self.kb_height
        self.kb_canvas.create_rectangle(x0, y0, x1, y1, fill=color)
        self.kb_canvas.create_text(
            (x0 + x1) / 2, (y0 + y1) / 2, text=letter, font=self.keyboard_font
        )

    def draw_keyboard(self):
        states = self.game.letter_states()
        for i in range(0, 26):
            letter = chr(i + 97)
            row = i // 13
            col = i % 13
            color = KEY_COLORS[states[letter]]
            self.draw_keyboard_key(row, col, letter, color)

    def submit_guess(self):
        try:
            self.game.guess("".join(self.current_guess))
        except InvalidGuess:
            self.invalid_guess = True
        self.reset_guess()

    def draw_hline(self, row, col0, col1, color):
        x0, y0 = self.get_coords(row, col0)
        y0 -= self.y_pad / 2
        x1 = x0 + (self.width + self.x_pad) * (col1 - col0)
        self.canvas.create_line(x0, y0, x1, y0, fill=color)

    def draw_input_cells(self):
        if self.input_cells:
            for entry in self.input_cells.keys():
                self.canvas.delete(entry)
        self.input_cells = {}
        i = len(self.game.guesses)
        unselected = Colors.WRONG if self.invalid_guess else Colors.DEFAULT
        for j in range(5):
            color = Colors.SELECTED if j == self.current_cell else unselected
            letter = self.current_guess[j]
            id = self.draw_letterbox(i, j, color=color, letter=letter)
            self.canvas.tag_bind(id, "<ButtonPress-1>", self.on_entry_click)
            self.input_cells[id] = j

    def draw_previous_guess(self, i):
        guess, response = self.game.guesses[i]
        _, at_least, _ = response
        at_least_count = [0] * 26
        for j, letter in enumerate(guess):
            color = Colors.DEFAULT
            if letter == self.game.solution[j]:
                color = Colors.CORRECT
            else:
                idx = ord(letter) - 97
                if at_least_count[idx] < at_least[idx]:
                    color = Colors.MISPLACED
                    at_least_count[idx] += 1

            self.draw_letterbox(i, j, letter=letter, color=color)

    def draw(self):
        self.canvas.delete("all")

        for i in range(len(self.game.guesses)):
            self.draw_previous_guess(i)

        # draw current guess
        i = len(self.game.guesses)
        if self.game.state != State.OPEN:
            self.show_solution = True

        if i < self.game.tries:
            if self.show_solution:
                for j in range(5):
                    self.draw_letterbox(i, j)
            else:
                self.draw_input_cells()
                self.invalid_guess = False

        # draw empty guesses remaining
        for i in range(len(self.game.guesses) + 1, self.game.tries):
            for j in range(5):
                self.draw_letterbox(i, j)

        self.draw_hline(self.game.tries, 0, 5, "black")

        # draw solution
        i = self.game.tries
        color = Colors.CORRECT if self.show_solution else Colors.DEFAULT
        for j in range(5):
            letter = self.game.solution[j] if self.show_solution else " "
            self.draw_letterbox(i, j, letter=letter, color=color)

        self.draw_keyboard()

    def on_entry_click(self, event):
        self.current_cell = self.input_cells[
            event.widget.find_closest(event.x, event.y)[0]
        ]
        self.draw_input_cells()

    def input_char(self, char):
        if self.game.state != State.OPEN:
            return
        if self.current_cell < 5:
            self.current_guess[self.current_cell] = char

    def input_clear(self):
        if self.game.state != State.OPEN:
            return
        self.input_char(" ")

    def input_advance(self):
        if self.game.state != State.OPEN:
            return
        if self.current_cell < 5:
            self.current_cell += 1

    def input_back(self):
        if self.game.state != State.OPEN:
            return
        if self.current_cell > 0:
            self.current_cell -= 1

    def undo(self):
        if self.game.guesses:
            self.game.guesses.pop()
        self.show_solution = False

    def on_keypress(self, event):
        if event.keysym == "BackSpace":
            self.input_back()
            self.input_clear()
            self.draw()
        elif event.keysym == "Return":
            self.submit_guess()
            self.draw()
        elif event.keysym == "Left":
            self.input_back()
            self.draw()
        elif event.keysym == "Right":
            self.input_advance()
            self.draw()
        elif event.char and ord(event.char) in range(ord("a"), ord("z") + 1):
            self.input_char(event.char)
            self.input_advance()
            self.draw()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", default=None)
    parser.add_argument("--tries", default=5, type=int)
    args = parser.parse_args()

    root = Tk()
    root.title("Untitled Word Game")

    # Game
    game = Game(tries=args.tries, solution=args.solution)
    game_frame = Frame(root)
    kb_frame = Frame(root)
    game_widget = GameWidget(game, game_frame, kb_frame)
    root.bind("<KeyPress>", game_widget.on_keypress)
    game_widget.draw()

    # Menu
    def new_game():
        game_widget.set_game(Game())
        game_widget.reset_canvas()
        game_widget.draw()

    def restart():
        game_widget.game.restart()
        game_widget.show_solution = False
        game_widget.reset_guess()
        game_widget.draw()

    def undo():
        game_widget.undo()
        game_widget.draw()

    def show_solution():
        game_widget.show_solution = True
        game_widget.draw()

    def solve(treshold):
        def solve_f():
            game = game_widget.game
            if game_widget.button_ok:
                game_widget.button_ok.destroy()
            solver = Solver(game)
            solver.guess(treshold)
            game_widget.draw()

        return solve_f

    menu = Frame(root)
    button_row = 0
    button_font = Font(size=12)
    button_width = sx(12)

    def menu_button(text, command):
        button = Button(
            menu,
            text=text,
            width=button_width,
            font=button_font,
            command=command,
        )
        nonlocal button_row
        button.grid(row=button_row, column=0, sticky=N + E)
        button_row += 1

    menu_button("NEW GAME", new_game)
    menu_button("RESTART", restart)
    menu_button("UNDO", undo)
    menu_button("GIVE UP", show_solution)
    menu_button("SOLVER (FAST/BAD)", solve(Treshold.FAST))
    menu_button("SOLVER (MEDIUM/GOOD)", solve(Treshold.GOOD))
    menu_button("SOLVER (SLOW/BEST)", solve(Treshold.BEST))
    menu_button("QUIT", lambda: sys.exit(0))

    # Title
    title = Frame(root)
    title_canvas = Canvas(title, width=sx(400), height=sy(50))
    title_canvas.create_text(
        sx(200), sy(30), text="Untitled Word Game", font=Font(size=30)
    )
    title_canvas.pack()

    # Frames Layout
    title.grid(row=0, column=0, columnspan=2)
    menu.grid(row=1, column=0, sticky=N + E, pady=sy(20), padx=sx(20))
    game_frame.grid(row=1, column=1, rowspan=2)
    kb_frame.grid(row=3, column=0, columnspan=2)

    root.mainloop()


if __name__ == "__main__":
    main()
