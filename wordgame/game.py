import random
from collections import defaultdict

from wordgame.words import WORDS


try:
    from wordgame.fastcheck import check
    print("Using fastcheck.")
except ImportError:

    def check(guess, solution):
        correct = []
        at_least = [0] * 26
        at_most = [5] * 26
        letters_count_guess = defaultdict(lambda: 0)
        letters_count_actual = defaultdict(lambda: 0)
        for i, (letter_guessed, letter_actual) in enumerate(
            zip(guess, solution)
        ):
            if letter_actual == letter_guessed:
                correct.append(i)
            else:
                letters_count_guess[letter_guessed] += 1
                letters_count_actual[letter_actual] += 1

        for letter, count_guess in letters_count_guess.items():
            count_actual = letters_count_actual[letter]
            if count_guess > count_actual:
                at_most[ord(letter) - 97] = count_actual
                at_least[ord(letter) - 97] = count_actual
            else:
                at_least[ord(letter) - 97] = count_guess

        return correct, at_least, at_most

    print("Could not import fastcheck, was it built with Cython?")
    print("You may try building it with: python setup.py build_ext --inplace")
    print("and re-installing the package.")
    print("Using slower check function.")


class GameFinished(Exception):
    pass


class InvalidGuess(Exception):
    pass


VALID_GUESSES = WORDS
VALID_GUESSES_SET = set(WORDS)
SOLUTIONS = VALID_GUESSES[:2315]


class State:
    OPEN = "open"
    SOLVED = "solved"
    FAILED = "failed"


class LetterState:
    EXACT = "exact"
    SOME = "some"
    NONE = "none"
    UNKNOWN = "unknown"


class Game:
    def __init__(self, tries=6, solution=None):
        self.tries = tries
        self.solution = solution if solution else random.choice(SOLUTIONS)
        self.guesses = []

    def guess(self, guess):
        if self.state != State.OPEN:
            raise GameFinished()
        if guess not in VALID_GUESSES_SET:
            raise InvalidGuess()
        response = check(guess, self.solution)
        self.guesses.append((guess, response))
        return response

    def restart(self):
        self.guesses = []

    @property
    def state(self):
        if self.guesses and self.guesses[-1][0] == self.solution:
            return State.SOLVED
        elif len(self.guesses) < self.tries:
            return State.OPEN
        else:
            return State.FAILED

    def letter_states(self):
        states = defaultdict(lambda: LetterState.UNKNOWN)
        for (guess, response) in self.guesses:
            correct, at_least, at_most = response
            for i, letter in enumerate(guess):
                if states[letter] in (LetterState.EXACT, LetterState.NONE):
                    continue
                if i in correct:
                    states[letter] = LetterState.EXACT
                elif at_least[ord(letter) - 97] > 0:
                    states[letter] = LetterState.SOME
                else:
                    states[letter] = LetterState.NONE

        return states
