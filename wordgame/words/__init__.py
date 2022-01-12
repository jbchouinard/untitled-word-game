def wordle():
    import wordgame.words.wordle

    return wordgame.words.wordle.WORDS


def scrabble5():
    import wordgame.words.scrabble5

    return wordgame.words.scrabble5.WORDS


def scrabble6():
    import wordgame.words.scrabble6

    return wordgame.words.scrabble6.WORDS


def scrabble7():
    import wordgame.words.scrabble7

    return wordgame.words.scrabble7.WORDS


def scrabble8():
    import wordgame.words.scrabble8

    return wordgame.words.scrabble8.WORDS


def dictionary5():
    import wordgame.words.dictionary5

    return wordgame.words.dictionary5.WORDS


def dictionary6():
    import wordgame.words.dictionary6

    return wordgame.words.dictionary6.WORDS


def dictionary7():
    import wordgame.words.dictionary7

    return wordgame.words.dictionary7.WORDS


def dictionary8():
    import wordgame.words.dictionary8

    return wordgame.words.dictionary8.WORDS


class WordSet:
    def __init__(self, loader, letter_count, top_n, first_guess):
        self.letter_count = letter_count
        self.top_n = top_n
        self.loader = loader
        self.first_guess = first_guess
        self._words = None
        self._words_set = None
        self._solutions = None
        self._solutions_set = None

    @property
    def words(self):
        if not self._words:
            self._words = self.loader()[:]
        return self._words

    @property
    def words_set(self):
        if not self._words_set:
            self._words_set = set(self.words)
        return self._words_set

    @property
    def solutions(self):
        if not self._solutions:
            self._solutions = self.loader()[: self.top_n]
        return self._solutions

    @property
    def solutions_set(self):
        if not self._solutions_set:
            self._solutions_set = set(self.solutions)
        return self._solutions_set


WORD_SETS = {
    "wordle": WordSet(wordle, 5, 2315, "tares"),
    "scrabble5": WordSet(scrabble5, 5, 2000, "tares"),
    "scrabble6": WordSet(scrabble6, 6, 3000, "salter"),
    "scrabble7": WordSet(scrabble7, 7, 4000, "saltier"),
    "scrabble8": WordSet(scrabble8, 8, 5000, "notaries"),
    "dictionary5": WordSet(dictionary5, 5, 2000, "tares"),
    "dictionary6": WordSet(dictionary6, 6, 3000, "salter"),
    "dictionary7": WordSet(dictionary7, 7, 4000, "saltier"),
    "dictionary8": WordSet(dictionary8, 8, 5000, "notaries"),
}
