import argparse
import time
from collections import defaultdict

from wordgame.game import check, Game, State
from wordgame.words import WORD_SETS


class Solver:
    def __init__(self, game):
        self.game = game
        self.possible_solutions = game.wordset.solutions[:]
        self.first_guess = True
        # Take into account pre-existing guesses on the game
        for (guess, response) in game.guesses:
            self.first_guess = False
            self.filter_solutions(guess, response)

    def filter_solutions(self, guess, response):
        self.possible_solutions = [
            soln
            for soln in self.possible_solutions
            if check(guess, soln, self.game.wordset.letter_count) == response
        ]

    def find_guess(self):
        best_guess = self.game.wordset.words[0]
        best_score = self.compute_score(best_guess)
        for guess in self.game.wordset.words[1:]:
            score = self.compute_score(guess)
            # Favor a guess which is a potential solution
            if (
                score == best_score
                and guess in self.possible_solutions
                and best_guess not in self.possible_solutions
            ):
                best_guess = guess
            elif score < best_score:
                best_guess, best_score = guess, score
        return best_guess

    def compute_score(self, guess):
        results = defaultdict(lambda: 0)
        for soln in self.possible_solutions:
            response = check(guess, soln, self.game.wordset.letter_count)
            results[response] += 1

        return sum(n ** 2 for n in results.values())

    def guess(self):
        # Precomputed best first move
        if self.first_guess:
            guess = self.game.wordset.first_guess
            self.first_guess = False
        else:
            guess = self.find_guess()
        response = self.game.guess(guess)
        self.filter_solutions(guess, response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--words", choices=WORD_SETS.keys(), default="wordle")
    args = parser.parse_args()

    wordset = WORD_SETS[args.words]

    n_trials = len(wordset.solutions)
    trials = wordset.solutions
    n_guesses = []
    n_failed = 0
    start_time = time.time()
    for i, soln in enumerate(trials, 1):
        game = Game(wordset, solution=soln)
        solver = Solver(game)
        while game.state == State.OPEN:
            solver.guess()
        n = len(game.guesses)
        if game.state == State.SOLVED:
            print(f"{i}/{n_trials} Solved {soln} in {n} guesses.")
            n_guesses.append(n)
        else:
            print(f"{i}/{n_trials} Failed to solve {soln}.")
            n_failed += 1

    elapsed = time.time() - start_time
    avg = sum(n_guesses) / len(n_guesses)
    avg_ms = 1000 * (elapsed / len(n_guesses))
    if n_failed:
        print(f"Failed to solve {n_failed} puzzles.")
    print(
        (
            f"Solved puzzles in average of {avg:.2f} guesses in {avg_ms:.1f}ms, "
            f"max of {max(n_guesses):d} guesses."
        )
    )


if __name__ == "__main__":
    main()
