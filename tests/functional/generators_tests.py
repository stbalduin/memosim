'''
Created on 01.10.2015

@author: tklingenberg
'''
import unittest

from memosim_garbage.generators import ConstantValue, ControllableValue,\
    Increment, Series


class Test(unittest.TestCase):
    
    # ControllableValue

    def test_ctrable_value_init_default(self):
        value = ControllableValue()
        self.assertEqual(0, value.value)

    def test_ctrable_value_init_with_value(self):
        value = ControllableValue(100.7)
        self.assertEqual(100.7, value.value)
        
    def test_ctrable_value_next(self):
        value = ControllableValue(-47.11)
        self.assertEqual(-47.11, value.next())
        
    def test_ctrable_value_copy(self):
        value = ControllableValue(100.7)
        value2 = value.copy()
        self.assertEqual(value, value2)
    
    def test_ctrable_value_neq(self):
        value = ControllableValue(100.7)
        value2 = ControllableValue(42)
        self.assertNotEqual(value, value2)
    
    def test_ctrable_value_modify(self):
        value = ControllableValue(42)
        value.value = 21
        self.assertEqual(21, value.value)
            
    # ConstantValue

    def test_const_value_init_default(self):
        value = ConstantValue()
        self.assertEqual(0, value.value)

    def test_const_value_init_with_value(self):
        value = ConstantValue(100.7)
        self.assertEqual(100.7, value.value)
        
    def test_const_value_next(self):
        value = ConstantValue(-47.11)
        self.assertEqual(-47.11, value.next())
        
    def test_const_value_copy(self):
        value = ConstantValue(100.7)
        value2 = value.copy()
        self.assertEqual(value, value2)
    
    def test_const_value_neq(self):
        value = ConstantValue(100.7)
        value2 = ConstantValue(42)
        self.assertNotEqual(value, value2)
        
    def test_const_value_modify(self):
        value = ConstantValue(42)
        with self.assertRaises(AttributeError):
            value.value = 21
        
    # Increment
    
    def test_increment_init_default(self):
        value = Increment()
        self.assertEqual(0, value.value)

    def test_increment_init_with_value(self):
        value = Increment(100.7)
        self.assertEqual(100.7, value.value)
            
    def test_increment_next(self):
        value = Increment(-47.11)
        self.assertEqual(-46.11, value.next())
    
    def test_increment_next_with_custom_stepsize(self):
        value = Increment(-47.11, 10)
        self.assertEqual(-37.11, value.next())
            
    def test_increment_copy(self):
        value = Increment(100.7)
        value2 = value.copy()
        self.assertEqual(value, value2)
    
    def test_increment_copy_and_step(self):
        value = Increment(100.7)
        value2 = value.copy()
        self.assertEqual(value.next(), value2.next())
        
    def test_increment_neq(self):
        value = Increment(100.7)
        value2 = Increment(42)
        self.assertNotEqual(value, value2)
        
    def test_increment_modify(self):
        value = Increment(42)
        with self.assertRaises(AttributeError):
            value.value = 21
        
    # Increment
    
    def test_series_init(self):
        data = list(range(5,10))
        value = Series(data)
        self.assertEqual(5, value.value)
        
    def test_series_next(self):
        data = list(range(5,10))
        value = Series(data)
        self.assertEqual(6, value.next())
        
    def test_series_copy(self):
        data = list(range(5,10))
        value = Series(data)
        value2 = value.copy()
        self.assertEqual(value, value2)
    
    def test_series_copy_and_step(self):
        data = list(range(5,10))
        value = Series(data)
        value2 = value.copy()
        self.assertEqual(value.next(), value2.next())
        
    def test_series_neq(self):
        data = list(range(5,10))
        value = Series(data)
        data2 = list(range(10))
        value2 = Series(data2)
        self.assertNotEqual(value, value2)
        
    def test_series_value_modify(self):
        data = list(range(5,10))
        value = Series(data)
        with self.assertRaises(AttributeError):
            value.value = 21
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()