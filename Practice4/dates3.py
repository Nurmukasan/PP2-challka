from datetime import datetime

current_datetime = datetime.now()
without_microseconds = current_datetime.replace(microsecond=0)

print("With microseconds:", current_datetime)
print("Without microseconds:", without_microseconds)