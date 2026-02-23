def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

a, b = map(int, input().split())
for value in squares(a, b):
    print(value)