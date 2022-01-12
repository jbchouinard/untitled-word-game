def frequencies():
    freqs = {}
    with open("frequency.txt", "r") as f:
        for line in f:
            word, freq = line.strip().split("\t")
            freq = int(freq)
            freqs[word] = freq
    return freqs


def matches(word, letter_count):
    if len(word) != letter_count:
        return False
    for letter in word:
        if letter < "a" or letter > "z":
            return False
    return True


def make_word_list(in_file, out_file, letter_count):
    freqs = frequencies()
    with open(in_file, "r") as f:
        words = [line.strip() for line in f]
    words = [w for w in words if matches(w, letter_count)]
    words.sort(key=lambda w: freqs.get(w, 0), reverse=True)
    with open(out_file, "w") as f:
        f.write("WORDS=[\n")
        for word in words:
            f.write(f"    '{word}',\n")
        f.write("]")


if __name__ == "__main__":
    make_word_list("scrabble.txt", "scrabble5.py", 5)
    make_word_list("scrabble.txt", "scrabble6.py", 6)
    make_word_list("scrabble.txt", "scrabble7.py", 7)
    make_word_list("scrabble.txt", "scrabble8.py", 8)
    make_word_list("dictionary.txt", "dictionary5.py", 5)
    make_word_list("dictionary.txt", "dictionary6.py", 6)
    make_word_list("dictionary.txt", "dictionary7.py", 7)
    make_word_list("dictionary.txt", "dictionary8.py", 8)
