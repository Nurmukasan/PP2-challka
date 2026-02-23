import math

n = int(input("Input number of sides: "))
side_length = float(input("Input the length of a side: "))

area = (n * side_length ** 2) / (4 * math.tan(math.pi / n))
print(f"The area of the polygon is: {int(area)}")