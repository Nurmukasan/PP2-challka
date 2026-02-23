def divisible_by_3_and_4(n):
    for i in range(0, n + 1, 12):
        yield str(i)

n = int(input())
print(' '.join(divisible_by_3_and_4(n)))