import argparse
import time

from wordgame.game import check, VALID_GUESSES, SOLUTIONS


class Treshold:
    BEST = 0
    GOOD = 1 / 8
    FAST = 1 / 4


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

    def find_guess(self, treshold):
        best_guess = VALID_GUESSES[0]
        best_n = len(self.possible_solutions)
        if best_n == 1:
            return self.possible_solutions[0]
        for i, guess in enumerate(VALID_GUESSES, 1):
            expected_n = self.compute_expected_n_solns(guess)
            if expected_n <= len(self.possible_solutions) * treshold:
                return guess
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
        ns = []
        for soln in self.possible_solutions:
            response = check(guess, soln)
            left = self.filter_solutions(
                self.possible_solutions, guess, response
            )
            ns.append(len(left))
        return sum(ns) / len(ns)

    def guess(self, treshold=0.5):
        # Precomputed best first move
        if self.first_guess:
            guess = "soare"
            self.first_guess = False
        else:
            guess = self.find_guess(treshold)
        response = self.game.guess(guess)
        self.possible_solutions = self.filter_solutions(
            self.possible_solutions, guess, response
        )


def main():
    from wordgame.game import Game, State, SOLUTIONS

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["best", "good", "fast"])
    args = parser.parse_args()

    treshold = {
        "best": Treshold.BEST,
        "good": Treshold.GOOD,
        "fast": Treshold.FAST,
    }[args.mode]

    n_guesses = []
    n_failed = 0

    start_time = time.time()
    ntotal = len(SOLUTIONS)
    for i, soln in enumerate(SOLUTIONS):
        print(f"solving game {i} of {ntotal} ({soln})")
        game = Game(solution=soln)
        solver = Solver(game)
        while game.state == State.OPEN:
            solver.guess(treshold)
        n = len(game.guesses)
        if game.state == State.SOLVED:
            n_guesses.append(n)
        else:
            n_failed += 1

    elapsed = time.time() - start_time
    avg = sum(n_guesses) / len(n_guesses)
    avg_secs = elapsed / len(n_guesses)
    if n_failed:
        print(f"Failed to solve {n_failed} puzzles.")
    print(
        (
            f"Solved puzzles in average of {avg:.2f} guesses, "
            f"max of {max(n_guesses):d} guesses, average of {avg_secs:.3f} seconds/puzzle"
        )
    )
    with open("n_guesses_{}.txt".format(args.mode), "w") as f:
        f.write(",".join((str(n) for n in n_guesses)))


if __name__ == "__main__":
    main()
