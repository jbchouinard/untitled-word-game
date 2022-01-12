import time
from collections import defaultdict

from wordgame.game import check, Game, State, VALID_GUESSES, SOLUTIONS


class Solver:
    def __init__(self, game):
        self.game = game
        self.possible_solutions = SOLUTIONS[:]
        self.first_guess = True
        # Take into account pre-existing guesses on the game
        for (guess, response) in game.guesses:
            self.first_guess = False
            self.filter_solutions(self.possible_solutions, guess, response)

    def filter_solutions(self, guess, response):
        self.possible_solutions = [
            soln for soln in self.possible_solutions if check(guess, soln) == response
        ]

    def find_guess(self):
        best_guess = VALID_GUESSES[0]
        best_score = self.compute_score(best_guess)
        for guess in VALID_GUESSES[1:]:
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
            response = check(guess, soln)
            results[response] += 1

        return sum(n ** 2 for n in results.values())

    def guess(self):
        # Precomputed best first move
        if self.first_guess:
            guess = "tares"
            self.first_guess = False
        else:
            guess = self.find_guess()
        response = self.game.guess(guess)
        self.filter_solutions(self.possible_solutions, guess, response)


def main():
    n_trials = 2315
    trials = SOLUTIONS[:n_trials]
    n_guesses = []
    n_failed = 0
    start_time = time.time()
    for i, soln in enumerate(trials, 1):
        game = Game(solution=soln)
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
    with open("n_guesses.txt", "w") as f:
        f.write(",".join((str(n) for n in n_guesses)))


if __name__ == "__main__":
    main()
