

import json
from pathlib import Path


DATA_FILE = Path(__file__).with_name("vehicles.txt")


class Vehicle:
    def __init__(self, vehicle_id, vehicle_type, model, rate, available=True):
        self.id = vehicle_id
        self.type = vehicle_type
        self.model = model
        self.rate = float(rate)
        self.available = bool(available)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "model": self.model,
            "rate": self.rate,
            "available": self.available,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["type"], data["model"], data["rate"], data["available"])


class RentalManagementSystem:
    def __init__(self):
        self.vehicles = []
        # Maps a rented vehicle ID to customer and rental duration.
        self.rentals = {}
        self.load_data()

    def load_data(self):
        if not DATA_FILE.exists():
            return
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
            self.vehicles = [Vehicle.from_dict(item) for item in data.get("vehicles", [])]
            self.rentals = data.get("rentals", {})
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            print(f"Could not load {DATA_FILE.name}: {error}")
            print("Starting with an empty vehicle list; the file will be replaced on the next save.")

    def save_data(self):
        data = {
            "vehicles": [vehicle.to_dict() for vehicle in self.vehicles],
            "rentals": self.rentals,
        }
        try:
            with DATA_FILE.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
        except OSError as error:
            print(f"Could not save data: {error}")

    def next_vehicle_id(self):
        numbers = []
        for vehicle in self.vehicles:
            if vehicle.id.startswith("V") and vehicle.id[1:].isdigit():
                numbers.append(int(vehicle.id[1:]))
        return f"V{max(numbers, default=0) + 1}"

    def find_vehicle(self, vehicle_id):
        return next((v for v in self.vehicles if v.id.lower() == vehicle_id.strip().lower()), None)

    def add_vehicle(self):
        vehicle_type = input("Type (e.g., Car, Bike): ").strip()
        model = input("Model: ").strip()
        if not vehicle_type or not model:
            print("Type and model cannot be empty.")
            return
        try:
            rate = float(input("Rate per day (Rs.): "))
            if rate <= 0:
                raise ValueError
        except ValueError:
            print("Please enter a positive number for the daily rate.")
            return
        vehicle = Vehicle(self.next_vehicle_id(), vehicle_type, model, rate)
        self.vehicles.append(vehicle)
        self.save_data()
        print(f"Vehicle added. ID: {vehicle.id} | {vehicle.type} | {vehicle.model} | Rs. {vehicle.rate:g}/day | Available")

    def show_vehicles(self, available_only=False):
        vehicles = [v for v in self.vehicles if v.available or not available_only]
        if not vehicles:
            print("No vehicles to display.")
            return
        print("\nID   | Type | Model | Rate/day | Status")
        print("-" * 55)
        for vehicle in vehicles:
            status = "Available" if vehicle.available else "Rented"
            print(f"{vehicle.id:<4} | {vehicle.type:<4} | {vehicle.model:<5} | Rs. {vehicle.rate:g} | {status}")

    def rent_vehicle(self):
        vehicle_id = input("Vehicle ID: ").strip()
        vehicle = self.find_vehicle(vehicle_id)
        if vehicle is None or not vehicle.available:
            print(f"Vehicle {vehicle_id} is not available.")
            return
        customer = input("Customer name: ").strip()
        if not customer:
            print("Customer name cannot be empty.")
            return
        try:
            days = int(input("Number of days: "))
            if days < 1:
                raise ValueError
        except ValueError:
            print("Days must be a whole number of 1 or more.")
            return
        bill = vehicle.rate * days
        discount_text = ""
        if days >= 7:
            bill *= 0.90
            discount_text = " 10% discount applied."
        vehicle.available = False
        self.rentals[vehicle.id] = {"customer": customer, "days": days}
        self.save_data()
        print(f"{vehicle.id} rented to {customer} for {days} days.{discount_text} Bill: Rs. {bill:g}")

    def return_vehicle(self):
        vehicle_id = input("Vehicle ID to return: ").strip()
        vehicle = self.find_vehicle(vehicle_id)
        if vehicle is None:
            print(f"Vehicle {vehicle_id} was not found.")
        elif vehicle.available:
            print(f"Vehicle {vehicle.id} is already available.")
        else:
            vehicle.available = True
            self.rentals.pop(vehicle.id, None)
            self.save_data()
            print(f"{vehicle.id} returned. Status: Available")

    def run(self):
        actions = {
            "1": self.add_vehicle,
            "2": self.rent_vehicle,
            "3": self.return_vehicle,
            "4": lambda: self.show_vehicles(available_only=True),
            "5": lambda: self.show_vehicles(available_only=False),
        }
        while True:
            print("\n=== Vehicle Rental Management System ===")
            print("1. Add vehicle\n2. Rent vehicle\n3. Return vehicle\n4. View available vehicles\n5. View all vehicles\n6. Exit")
            choice = input("Choose an option: ").strip()
            if choice == "6":
                print("Goodbye!")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid option. Choose a number from 1 to 6.")


if __name__ == "__main__":
    RentalManagementSystem().run()
