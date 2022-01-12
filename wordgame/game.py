import random
from collections import defaultdict

from wordgame.words import WORD_SETS


try:
    from wordgame.fastcheck import check

    print("Using fastcheck.")
except ImportError:

    def check(guess, solution, _letter_count):
        result = []
        count_nonexact_guess = defaultdict(lambda: 0)
        count_nonexact_solution = defaultdict(lambda: 0)

        for (letter_solution, letter_guess) in zip(solution, guess):
            if letter_solution != letter_guess:
                count_nonexact_solution[letter_solution] += 1

        for (letter_solution, letter_guess) in zip(solution, guess):
            if letter_solution == letter_guess:
                result.append(LetterState.EXACT)
            elif (
                count_nonexact_guess[letter_guess]
                < count_nonexact_solution[letter_guess]
            ):
                result.append(LetterState.SOME)
                count_nonexact_guess[letter_guess] += 1
            else:
                result.append(LetterState.NONE)

        return tuple(result)

    print("Could not import fastcheck, was it built with Cython?")
    print("You may try building it with: python setup.py build_ext --inplace")
    print("and re-installing the package.")
    print("Using slower check function.")


class GameFinished(Exception):
    pass


class InvalidGuess(Exception):
    pass


class State:
    OPEN = 0
    SOLVED = 1
    FAILED = 2


class LetterState:
    UNKNOWN = 0
    EXACT = 1
    SOME = 2
    NONE = 3


class Game:
    def __init__(self, wordset, tries=6, solution=None):
        self.wordset = wordset
        self.tries = tries
        self.solution = solution if solution else random.choice(wordset.solutions)
        self.guesses = []

    def guess(self, guess):
        if self.state != State.OPEN:
            raise GameFinished()
        if guess not in self.wordset.words_set:
            print(self.wordset.words_set)
            raise InvalidGuess(guess)
        response = check(guess, self.solution, self.wordset.letter_count)
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
            for (letter, rstate) in zip(guess, response):
                lstate = states[letter]
                if lstate == LetterState.EXACT:
                    continue
                elif rstate == LetterState.EXACT:
                    states[letter] = rstate
                elif lstate == LetterState.SOME:
                    continue
                else:
                    states[letter] = rstate

        return states
