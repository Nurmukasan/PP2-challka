def squares_generator(N):
    for i in range(1, N + 1):
        yield i * i

N = int(input())
for square in squares_generator(N):
    print(square)