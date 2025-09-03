"""
Examples demonstrating list type configurations in confkit.

This example shows:
1. Working with lists of different data types
2. Handling lists with special characters
3. Escaping in lists
4. Empty lists and list validation

Run with: python list_types.py
"""

from configparser import ConfigParser
from pathlib import Path

from confkit import Config
from confkit.data_types import List, String

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))
List.escape_char = "\\"  # Set escape character for lists, these are also the default.
List.separator = ","  # Set separator character for lists, these are also the default.

class ListConfig:
    """Configuration class demonstrating list types."""
    
    # Lists of different data types
    string_list = Config(List(["red", "green", "blue"]))
    int_list = Config(List([1, 2, 3, 4, 5]))
    float_list = Config(List([1.1, 2.2, 3.3, 4.4]))
    bool_list = Config(List([True, False, True]))
    
    # Lists with special characters
    paths_list = Config(List(["/path/to/file1", "C:\\path\\to\\file2"]))
    
    # Lists with commas in values (will be escaped)
    complex_list = Config(List(["item1", "item,with,commas", "normal item"]))
    
    # List with empty values
    with_empty = Config(List(["", "middle", ""]))
    
    # Empty list with explicit data type
    empty_list = Config(List([], data_type=String("")))
