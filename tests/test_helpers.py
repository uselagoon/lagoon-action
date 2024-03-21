import unittest

from helpers import parse_key_value_string, build_buildvar_strings

# This class is used to test the helper functions that process incoming 
class TestBuildVarFunctions(unittest.TestCase):

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

    def test_parse_key_value_string_empty_string(self):
        # Test parsing with values containing '='
        input_string = ""
        expected_output = {}
        result = parse_key_value_string(input_string)
        self.assertEqual(result, expected_output)

    def test_parse_key_value_string_invalid_format(self):
        # Test invalid input format
        invalid_input = "key1=val1,key2=val2,key3"  # Missing '=' in key-value pair
        with self.assertRaises(ValueError):
            parse_key_value_string(invalid_input)


    def test_build_buildvar_strings(self):
        # Test building buildvar strings
        key_value_map = {
            'key1': 'val1',
            'key2': 'encoded_val==',
            'key3': 'val3',
            'key4': 'comma',
            'val5': 'val=with=equals'
        }
        expected_output = [
            "--buildvar key1=val1",
            "--buildvar key2=encoded_val==",
            "--buildvar key3=val3",
            "--buildvar key4=comma",
            "--buildvar val5=val=with=equals"
        ]
        result = build_buildvar_strings(key_value_map)
        self.assertEqual(result, expected_output)

    def test_build_buildvar_strings_single_entry(self):
        # Test building buildvar string for a single entry
        key_value_map = {'key1': 'val1'}
        expected_output = ["--buildvar key1=val1"]
        result = build_buildvar_strings(key_value_map)
        self.assertEqual(result, expected_output)
        self.assertEqual("--buildvar key1=val1", ' '.join(result))
    
    def test_build_input_integration(self):
        # Parsing through to single argument
        input_string = "key1=val1,key2=val2,key3=val3"
        keyvalmap = parse_key_value_string(input_string)
        stringMap = build_buildvar_strings(keyvalmap)
        self.assertEqual("--buildvar key1=val1 --buildvar key2=val2 --buildvar key3=val3", ' '.join(stringMap))


    def test_build_buildvar_strings_empty_entry(self):
        # Test building buildvar string for an empty entry
        key_value_map = {}
        expected_output = []
        result = build_buildvar_strings(key_value_map)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()