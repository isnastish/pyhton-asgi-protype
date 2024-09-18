import functools # unused
from loguru import logger 

from rangetest import rangetest, advance_rangetest 


class Person:
    def __init__(self, name: str, job_title: str, salary: float = 0.0) -> None:
        self.name = name
        self.job_title = job_title
        self.salary = salary
    
    @property
    def last_name(self) -> str:
        """Get person's last name"""
        return self.name.split(sep=" ", maxsplit=1)[-1]  
    
    @property
    def first_name(self) -> str:
        """Get person's first name"""
        return self.name.split(sep=" ", maxsplit=1)[0]
    
    @property
    def annual_income(self) -> float:
        """Get annual income"""
        return self.salary * 12
    
    def give_raise(self, percent: float) -> None:
        """Give salary raise."""
        if percent < 0.0 or percent > 1.0:
            # TypeError or ValueError
            raise TypeError("Invalid percentage range")
        self.salary = self.salary * (1.0 + percent) 
    
    @rangetest([1, 0.0, 1.0])
    def give_raise_range_check(self, percent: float) -> None:
        self.salary = self.salary * (1.0 + percent) 

    def __str__(self) -> str:
        logger.info("Person's __str__ method called")
        return f"[Person: {self.name}, {self.job_title}, {self.salary}]"
    
    def __repr__(self) -> str:
        logger.info("Person's __repr__ method called")
    

if __name__ == '__main__':
    person = Person("John Doe", "Accountant", 67000)

    print(person)
    print(person.first_name)
    print(person.last_name)

    print(f"Before raise: {person.salary}")
    person.give_raise(0.15)
    print(f"After raise: {person.salary}")

    print(f"annual income: {person.annual_income}SEK")

    person.give_raise_range_check(.10)

    # invalid raise
    try:
        person.give_raise_range_check(-1.0)
    except TypeError as ex:
        logger.error(f"Exception {str(ex)}")
        