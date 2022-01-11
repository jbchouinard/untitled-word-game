def check(guess, solution):
    correct = []

    cdef int at_least[26]
    cdef int at_most[26]
    cdef int count_guess[26]
    cdef int count_actual[26]
    cdef int i
    for i in range(0, 26):
        at_least[i] = 0
        at_most[i] = 5
        count_guess[i] = 0
        count_actual[i] = 0

    cdef int guessarr[5]
    cdef int solnarr[5]
    for i in range(0, 5):
        guessarr[i] = ord(guess[i]) - 97
        solnarr[i] = ord(solution[i]) - 97

    for i in range(0, 5):
        if guessarr[i] == solnarr[i]:
            correct.append(i)
        else:
            count_guess[guessarr[i]] += 1
            count_actual[solnarr[i]] += 1

    for i in range(0, 26):
        if count_guess[i] == 0 and count_actual[i] == 0:
            continue
        if count_guess[i] > count_actual[i]:
            at_most[i] = count_actual[i]
            at_least[i] = count_actual[i]
        else:
            at_least[i] = count_guess[i]

    return (correct, at_least, at_most)
