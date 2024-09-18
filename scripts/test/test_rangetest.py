from loguru import logger
from unittest import TestCase  

from ..rangetest import rangetest, advance_rangetest


class RangesDecorateTestSuite(TestCase):
    def test_basic_rangetest(self):
        """Test basic rangetest decorator"""
        self.assertEqual("hello,world", "".join(["h", "e", "l", "l", "o", ",", "w", "o", "r", "l", "d"]))
        
        @rangetest([1, 1, 12])
        def valid_month(index: int) -> None:
            mapping: dict[int, str] = {
                1: "January", 
                2: "February", 
                3: "May", 
                4: "April", 
                5: "March", 
                6: "June", 
                7: "July", 
                8: "August", 
                9: "September", 
                10: "October", 
                11: "November", 
                12: "December", 
            }

            # Could throw out of range without rangetest 
            logger.info({"month": mapping[index]})

        @rangetest([1, 0.0, 1.0]) # 1 is the position of the argument
        def give_raise(salary: float, percent: float) -> None:
            raised_salary = salary * (1 + percent)
            logger.info({"raise_salary": raised_salary})

        with self.assertRaises(TypeError) as ex:
            _ = ex
            give_raise(48000, 12)
    

    def test_advance_range_test(self):
        """Test advanced range test"""
        @advance_rangetest(age=(0, 100))
        def pers_info(name: str, age: int) -> None:
            logger.info(f"{name} is {age} years old")

        with self.assertRaises(TypeError) as exc:
            pers_info("Ivan", 444)

            
