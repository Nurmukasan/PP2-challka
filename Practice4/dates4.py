from datetime import datetime

date1 = datetime(2025, 1, 1, 12, 0, 0)
date2 = datetime(2025, 1, 3, 14, 30, 0)

difference = date2 - date1
difference_seconds = difference.total_seconds()

print(f"Date 1: {date1}")
print(f"Date 2: {date2}")
print(f"Difference in seconds: {difference_seconds}")