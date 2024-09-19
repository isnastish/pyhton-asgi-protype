from loguru import logger
from unittest import TestCase
from string import hexdigits

from ..rangetest import typecheck


class TypecheckTestSuite(TestCase):
    def test_simple_typecheck(self):
        """Test simple typecheck""" 

        @typecheck(name=str, age=int, salary=float)
        def func(name, age, salary) -> None:
            print(f"Person with {name} is {age} years old, has salary {salary}")
        
        # a should be of type int, and c should be of type float
        # @typecheck(a=int, c=float)
        # def func(a, b, c, d) -> None:
            # print(f"{a=}, {b=}, {c=}, {d=}")
        
        func("Adam", 23, 5600.5)
    
    def test_get_index_by_value(self):
        """Test get index by name"""
        arr = [c.capitalize() for c in hexdigits] 
        a_index = arr.index('A')
        self.assertEqual(a_index, 10)

        with self.assertRaises(ValueError) as exc:
            arr.index("t")