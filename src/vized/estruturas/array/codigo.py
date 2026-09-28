"""Array: ordenação por bolha."""


def bubble_sort(v):
    n = len(v)
    for passada in range(n - 1):
        # a cada passada, o maior "afunda"
        for j in range(n - 1 - passada):
            if v[j] > v[j + 1]:
                v[j], v[j + 1] = v[j + 1], v[j]
    return v
