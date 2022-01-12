UNKNOWN = 0
EXACT = 1
SOME = 2
NONE = 3


def check(guess, solution):
    result = []
    cdef int guessarr[5]
    cdef int solnarr[5]
    cdef int count_nonexact_guess[26]
    cdef int count_nonexact_solution[26]
    cdef int i
    for i in range(0, 26):
        count_nonexact_guess[i] = 0
        count_nonexact_solution[i] = 0

    for i in range(0, 5):
        guessarr[i] = ord(guess[i]) - 97
        solnarr[i] = ord(solution[i]) - 97

    for i in range(0, 5):
        if guessarr[i] != solnarr[i]:
            count_nonexact_solution[solnarr[i]] += 1

    for i in range(0, 5):
        if guessarr[i] == solnarr[i]:
            result.append(EXACT)
        elif count_nonexact_guess[guessarr[i]] < count_nonexact_solution[guessarr[i]]:
            result.append(SOME)
        else:
            result.append(NONE)

    return tuple(result)
