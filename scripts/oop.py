from loguru import logger
from typing import TYPE_CHECKING


class Person:
    def __init__(self, name: str, age: int, address: str, email: str) -> None:
        logger.info("Person's __init__ method")
        self.name = name
        self.age = age
        self.address = address
        self.email = email
    
    def __str__(self) -> str:
        # Method is called when an object is converted to a string
        logger.info("Person's __str__ method")
        return f"{self.name}: age: {self.age}, address: {self.address}, email: {self.email}"
    
    def __eq__(self, other: "Person") -> bool:
        logger.info("Person __eq__ operator")
        return (self.name == other.name and self.age == other.age and 
            self.address == other.address and self.email == other.email)


class Employee(Person):
    def __init__(self, name: str, age: int, address: str, email: str, title: str, employment_id: int, salary: float) -> None:
        super().__init__(name, age, address, email)
        self.title = title
        self._employment_id = employment_id 
        self.salary = salary

    @property
    def id(self) -> int:
        return self._employment_id
    
    def annual_salary(self) -> float:
        return self.salary * 12
    
    def raw_salary(self, tax_percent: float) -> float:
        # self.salary = 100%
        # x = 33% 
        if tax_percent < 0 or tax_percent > 100: 
            raise ValueError(f"tax percent out of range {tax_percent}")

        return self.salary - (self.salary * tax_percent / 100)  
    
    def __eq__(self, other: "Employee") -> bool:
        # method is invoked when a == b is evaluated
        logger.info("Invoke __eq__ method on Employee")
        return super().__eq__(other)
    
    def __add__(self, other: "Employee") -> "Employee":
        logger.info("__add__ method is invoked")
        total_salary = self.salary + other.salary
        return Employee(other.name, other.age, other.address, other.email, other.title, other._employment_id, total_salary)


class Counter:
    _count: int = 0

    def __init__(self) -> None:
        Counter._count += 1
        logger.info({"counter": Counter._count})
    
    def get_count(self) -> int:
        return Counter._count


class FirstClass:
    def set_data(self, data: int) -> None:
        self.data = data
    
    def display(self) -> None:
        print(f"FirstClass's data: {self.data}")


class SecondClass(FirstClass):
    # set_data method is inherited

    def display(self) -> None:
        print(f"SecondClass's data {self.data}")


def run_script() -> None:
    """Run the testing script"""
    accountant = Person("Boris", 24, "Yew York city, 56", "boris@gmail.com")
    obj_str = str(accountant)
    print(obj_str)

    first_employee = Employee("Susan", 56, "Vest Abbey", "susan@gmail.com", "Developer", 44, 40000)
    print(first_employee.id)
    print(f"base salary: {first_employee.raw_salary(30)}")

    second_employee = Employee("Brad", 25, "Unknown", "brad@gmail.com", "Developer", 55, 77000)
    try:
        # simulate ValueError
        second_employee.raw_salary(116)
    except ValueError as ex:
        logger.error({"ex": str(ex)}) # call to __str__ method
    
    c0 = Counter()
    c1 = Counter()
    c2 = Counter()

    print(f"count: {c2.get_count()}")

    z = SecondClass()
    z.set_data(56)
    z.display()

    # summing up salaries
    third_employee = first_employee + second_employee
    print(f"third_employee salary: {third_employee.salary}")


if __name__ == '__main__':
    run_script()


