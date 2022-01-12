import time
from collections import defaultdict

from wordgame.game import check, Game, State, VALID_GUESSES, SOLUTIONS


class Solver:
    def __init__(self, game):
        self.game = game
        self.possible_solutions = SOLUTIONS[:]
        self.first_guess = True
        if game.guesses:
            self.first_guess = False
            for (guess, response) in game.guesses:
                self.possible_solutions = self.filter_solutions(
                    self.possible_solutions, guess, response
                )
        else:
            self.first_guess = True

    def filter_solutions(self, solns, guess, response):
        kept = []
        for soln in solns:
            if check(guess, soln) == response:
                kept.append(soln)
        return kept

    def find_guess(self):
        best_guess = VALID_GUESSES[0]
        best_n = len(self.possible_solutions)
        if best_n == 1:
            return self.possible_solutions[0]
        for i, guess in enumerate(VALID_GUESSES, 1):
            expected_n = self.compute_expected_n_solns(guess)
            # Favor a guess which is a potential solution
            if (
                expected_n == best_n
                and best_guess not in self.possible_solutions
                and guess in self.possible_solutions
            ):
                best_guess = guess
            elif expected_n < best_n:
                best_guess = guess
                best_n = expected_n
        return best_guess

    def compute_expected_n_solns(self, guess):
        results = defaultdict(lambda: 0)
        for soln in self.possible_solutions:
            response = check(guess, soln)
            results[response] += 1

        summ = 0
        count = 0
        for n in results.values():
            summ += n * n
            count += n

        return summ / count

    def guess(self):
        # Precomputed best first move
        if self.first_guess:
            guess = "tares"
            self.first_guess = False
        else:
            guess = self.find_guess()
        response = self.game.guess(guess)
        self.possible_solutions = self.filter_solutions(
            self.possible_solutions, guess, response
        )


def main():
    n_trials = 2315
    trials = SOLUTIONS[:n_trials]
    n_guesses = []
    n_failed = 0
    start_time = time.time()
    for i, soln in enumerate(trials):
        print(f"Solving game {i} of {n_trials} ({soln}).")
        game = Game(solution=soln)
        solver = Solver(game)
        while game.state == State.OPEN:
            solver.guess()
        n = len(game.guesses)
        if game.state == State.SOLVED:
            n_guesses.append(n)
        else:
            n_failed += 1

    elapsed = time.time() - start_time
    avg = sum(n_guesses) / len(n_guesses)
    avg_ms = 1000 * (elapsed / len(n_guesses))
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
