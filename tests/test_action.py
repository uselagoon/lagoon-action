import unittest

from action import parse_key_value_string

class TestActionFunctions(unittest.TestCase):

    def test_parse_key_value_string(self):
        input_string = "key1=val1,key2=val2,key3=val3"
        expected_output = {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
        result = parse_key_value_string(input_string)
        self.assertEqual(result, expected_output)
    
    def test_parse_key_value_string_with_equals_in_value(self):
        # Test parsing with values containing '='
        input_string = "key1=val1,key2=encoded_val==,key3=val3"
        expected_output = {'key1': 'val1', 'key2': 'encoded_val==', 'key3': 'val3'}
        result = parse_key_value_string(input_string)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()