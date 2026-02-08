class Engine:
    def start(self):
        return "Engine started"

class ElectricMotor:
    def charge(self):
        return "Battery charging"

class Car(Engine):
    def drive(self):
        return "Car is moving"

class HybridCar(Car, ElectricMotor):
    def eco_mode(self):
        return "Eco mode activated"

hybrid = HybridCar()
print(hybrid.start())
print(hybrid.drive())
print(hybrid.charge())
print(hybrid.eco_mode())
print(HybridCar.__mro__)