from importlib import import_module


class WordSet:
    def __init__(self, name, letter_count, top_n, first_guess):
        self.letter_count = letter_count
        self.top_n = top_n
        self.name = name
        self.first_guess = first_guess
        self._words = None
        self._words_set = None
        self._solutions = None
        self._solutions_set = None

    def load(self):
        mod = import_module(f"wordgame.words.{self.name}")
        return mod.WORDS

    @property
    def words(self):
        if not self._words:
            self._words = self.load()[:]
        return self._words

    @property
    def words_set(self):
        if not self._words_set:
            self._words_set = set(self.words)
        return self._words_set

    @property
    def solutions(self):
        if not self._solutions:
            self._solutions = self.load()[: self.top_n]
        return self._solutions

    @property
    def solutions_set(self):
        if not self._solutions_set:
            self._solutions_set = set(self.solutions)
        return self._solutions_set


WORD_SETS = {
    "wordle": WordSet("wordle", 5, 2315, "tares"),
    "scrabble (5 letters)": WordSet("scrabble5", 5, 2000, "tares"),
    "dictionary (5 letters)": WordSet("dictionary5", 5, 2000, "tares"),
    "scrabble (4 letters)": WordSet("scrabble4", 4, 2000, "sale"),
    "scrabble (6 letters)": WordSet("scrabble6", 6, 3000, "salter"),
    "scrabble (7 letters)": WordSet("scrabble7", 7, 4000, "saltier"),
    "scrabble (8 letters)": WordSet("scrabble8", 8, 5000, "notaries"),
    "dictionary (4 letters)": WordSet("dictionary4", 4, 2000, "sale"),
    "dictionary (6 letters)": WordSet("dictionary6", 6, 3000, "salter"),
    "dictionary (7 letters)": WordSet("dictionary7", 7, 4000, "saltier"),
    "dictionary (8 letters)": WordSet("dictionary8", 8, 5000, "notaries"),
}
