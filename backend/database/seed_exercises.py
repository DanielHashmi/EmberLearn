"""Seed exercises for all Python topics."""

import uuid
from datetime import datetime

# Exercise data covering all 8 Python topics
EXERCISES = [
    # Topic 1: Basics (Variables & Types)
    {
        "id": str(uuid.uuid4()),
        "title": "Hello World",
        "description": "Write a function that returns the string 'Hello, World!'",
        "difficulty": "easy",
        "topic_slug": "basics",
        "topic_name": "Variables & Types",
        "starter_code": '''def hello_world():
    # Return the greeting
    pass''',
        "solution": '''def hello_world():
    return "Hello, World!"''',
        "test_cases": [
            {"input": "hello_world()", "expected": "'Hello, World!'"}
        ],
        "estimated_time": 5
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Variable Swap",
        "description": "Write a function that swaps two variables and returns them as a tuple.",
        "difficulty": "easy",
        "topic_slug": "basics",
        "topic_name": "Variables & Types",
        "starter_code": '''def swap(a, b):
    # Swap a and b, return as tuple
    pass''',
        "solution": '''def swap(a, b):
    return (b, a)''',
        "test_cases": [
            {"input": "swap(1, 2)", "expected": "(2, 1)"},
            {"input": "swap('a', 'b')", "expected": "('b', 'a')"}
        ],
        "estimated_time": 5
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Type Checker",
        "description": "Write a function that returns the type name of the input as a string.",
        "difficulty": "easy",
        "topic_slug": "basics",
        "topic_name": "Variables & Types",
        "starter_code": '''def get_type_name(value):
    # Return the type name as string
    pass''',
        "solution": '''def get_type_name(value):
    return type(value).__name__''',
        "test_cases": [
            {"input": "get_type_name(42)", "expected": "'int'"},
            {"input": "get_type_name('hello')", "expected": "'str'"},
            {"input": "get_type_name([1,2,3])", "expected": "'list'"}
        ],
        "estimated_time": 5
    },
    
    # Topic 2: Control Flow
    {
        "id": str(uuid.uuid4()),
        "title": "FizzBuzz",
        "description": "Return 'Fizz' for multiples of 3, 'Buzz' for 5, 'FizzBuzz' for both, else the number.",
        "difficulty": "easy",
        "topic_slug": "control-flow",
        "topic_name": "Control Flow",
        "starter_code": '''def fizzbuzz(n):
    # Implement FizzBuzz logic
    pass''',
        "solution": '''def fizzbuzz(n):
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return n''',
        "test_cases": [
            {"input": "fizzbuzz(3)", "expected": "'Fizz'"},
            {"input": "fizzbuzz(5)", "expected": "'Buzz'"},
            {"input": "fizzbuzz(15)", "expected": "'FizzBuzz'"},
            {"input": "fizzbuzz(7)", "expected": "7"}
        ],
        "estimated_time": 10
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Sum of Range",
        "description": "Calculate the sum of all integers from 1 to n (inclusive).",
        "difficulty": "easy",
        "topic_slug": "control-flow",
        "topic_name": "Control Flow",
        "starter_code": '''def sum_range(n):
    # Sum numbers from 1 to n
    pass''',
        "solution": '''def sum_range(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total''',
        "test_cases": [
            {"input": "sum_range(5)", "expected": "15"},
            {"input": "sum_range(10)", "expected": "55"},
            {"input": "sum_range(1)", "expected": "1"}
        ],
        "estimated_time": 5
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Count Vowels",
        "description": "Count the number of vowels (a, e, i, o, u) in a string.",
        "difficulty": "medium",
        "topic_slug": "control-flow",
        "topic_name": "Control Flow",
        "starter_code": '''def count_vowels(text):
    # Count vowels in text
    pass''',
        "solution": '''def count_vowels(text):
    vowels = "aeiouAEIOU"
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    return count''',
        "test_cases": [
            {"input": "count_vowels('hello')", "expected": "2"},
            {"input": "count_vowels('AEIOU')", "expected": "5"},
            {"input": "count_vowels('xyz')", "expected": "0"}
        ],
        "estimated_time": 10
    },
    
    # Topic 3: Data Structures
    {
        "id": str(uuid.uuid4()),
        "title": "List Sum",
        "description": "Calculate the sum of all numbers in a list.",
        "difficulty": "easy",
        "topic_slug": "data-structures",
        "topic_name": "Data Structures",
        "starter_code": '''def list_sum(numbers):
    # Sum all numbers in the list
    pass''',
        "solution": '''def list_sum(numbers):
    return sum(numbers)''',
        "test_cases": [
            {"input": "list_sum([1, 2, 3, 4, 5])", "expected": "15"},
            {"input": "list_sum([])", "expected": "0"},
            {"input": "list_sum([10])", "expected": "10"}
        ],
        "estimated_time": 5
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Unique Elements",
        "description": "Return a list of unique elements from the input list, preserving order.",
        "difficulty": "medium",
        "topic_slug": "data-structures",
        "topic_name": "Data Structures",
        "starter_code": '''def unique_elements(lst):
    # Return unique elements
    pass''',
        "solution": '''def unique_elements(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result''',
        "test_cases": [
            {"input": "unique_elements([1, 2, 2, 3, 1])", "expected": "[1, 2, 3]"},
            {"input": "unique_elements(['a', 'b', 'a'])", "expected": "['a', 'b']"}
        ],
        "estimated_time": 10
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Word Frequency",
        "description": "Return a dictionary with word frequencies from a list of words.",
        "difficulty": "medium",
        "topic_slug": "data-structures",
        "topic_name": "Data Structures",
        "starter_code": '''def word_frequency(words):
    # Count word frequencies
    pass''',
        "solution": '''def word_frequency(words):
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq''',
        "test_cases": [
            {"input": "word_frequency(['a', 'b', 'a'])", "expected": "{'a': 2, 'b': 1}"},
            {"input": "word_frequency([])", "expected": "{}"}
        ],
        "estimated_time": 10
    },
    
    # Topic 4: Functions
    {
        "id": str(uuid.uuid4()),
        "title": "Factorial",
        "description": "Calculate the factorial of n using recursion.",
        "difficulty": "medium",
        "topic_slug": "functions",
        "topic_name": "Functions",
        "starter_code": '''def factorial(n):
    # Calculate n! recursively
    pass''',
        "solution": '''def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)''',
        "test_cases": [
            {"input": "factorial(5)", "expected": "120"},
            {"input": "factorial(0)", "expected": "1"},
            {"input": "factorial(1)", "expected": "1"}
        ],
        "estimated_time": 10
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Lambda Filter",
        "description": "Use a lambda to filter even numbers from a list.",
        "difficulty": "medium",
        "topic_slug": "functions",
        "topic_name": "Functions",
        "starter_code": '''def filter_evens(numbers):
    # Use filter with lambda
    pass''',
        "solution": '''def filter_evens(numbers):
    return list(filter(lambda x: x % 2 == 0, numbers))''',
        "test_cases": [
            {"input": "filter_evens([1, 2, 3, 4, 5, 6])", "expected": "[2, 4, 6]"},
            {"input": "filter_evens([1, 3, 5])", "expected": "[]"}
        ],
        "estimated_time": 10
    },
    
    # Topic 5: OOP
    {
        "id": str(uuid.uuid4()),
        "title": "Rectangle Class",
        "description": "Create a Rectangle class with width, height, and an area method.",
        "difficulty": "medium",
        "topic_slug": "oop",
        "topic_name": "Object-Oriented Programming",
        "starter_code": '''class Rectangle:
    def __init__(self, width, height):
        # Initialize width and height
        pass
    
    def area(self):
        # Return the area
        pass''',
        "solution": '''class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height''',
        "test_cases": [
            {"input": "Rectangle(3, 4).area()", "expected": "12"},
            {"input": "Rectangle(5, 5).area()", "expected": "25"}
        ],
        "estimated_time": 15
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Counter Class",
        "description": "Create a Counter class with increment, decrement, and get_value methods.",
        "difficulty": "easy",
        "topic_slug": "oop",
        "topic_name": "Object-Oriented Programming",
        "starter_code": '''class Counter:
    def __init__(self):
        # Initialize counter to 0
        pass
    
    def increment(self):
        pass
    
    def decrement(self):
        pass
    
    def get_value(self):
        pass''',
        "solution": '''class Counter:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1
    
    def decrement(self):
        self.value -= 1
    
    def get_value(self):
        return self.value''',
        "test_cases": [
            {"input": "c = Counter(); c.increment(); c.increment(); c.get_value()", "expected": "2"},
            {"input": "c = Counter(); c.decrement(); c.get_value()", "expected": "-1"}
        ],
        "estimated_time": 10
    },
    
    # Topic 6: Files
    {
        "id": str(uuid.uuid4()),
        "title": "Parse CSV Line",
        "description": "Parse a CSV line into a list of values.",
        "difficulty": "easy",
        "topic_slug": "files",
        "topic_name": "File Handling",
        "starter_code": '''def parse_csv_line(line):
    # Split by comma
    pass''',
        "solution": '''def parse_csv_line(line):
    return line.split(',')''',
        "test_cases": [
            {"input": "parse_csv_line('a,b,c')", "expected": "['a', 'b', 'c']"},
            {"input": "parse_csv_line('1,2,3')", "expected": "['1', '2', '3']"}
        ],
        "estimated_time": 5
    },
    {
        "id": str(uuid.uuid4()),
        "title": "JSON to Dict",
        "description": "Parse a JSON string into a Python dictionary.",
        "difficulty": "easy",
        "topic_slug": "files",
        "topic_name": "File Handling",
        "starter_code": '''import json

def parse_json(json_str):
    # Parse JSON string
    pass''',
        "solution": '''import json

def parse_json(json_str):
    return json.loads(json_str)''',
        "test_cases": [
            {"input": '''parse_json('{"name": "Alice"}')''', "expected": "{'name': 'Alice'}"},
            {"input": '''parse_json('{"x": 1, "y": 2}')''', "expected": "{'x': 1, 'y': 2}"}
        ],
        "estimated_time": 5
    },
    
    # Topic 7: Errors
    {
        "id": str(uuid.uuid4()),
        "title": "Safe Division",
        "description": "Divide two numbers, returning None if division by zero.",
        "difficulty": "easy",
        "topic_slug": "errors",
        "topic_name": "Error Handling",
        "starter_code": '''def safe_divide(a, b):
    # Handle division by zero
    pass''',
        "solution": '''def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None''',
        "test_cases": [
            {"input": "safe_divide(10, 2)", "expected": "5.0"},
            {"input": "safe_divide(10, 0)", "expected": "None"}
        ],
        "estimated_time": 5
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Safe Int Parse",
        "description": "Parse a string to int, returning a default value on error.",
        "difficulty": "easy",
        "topic_slug": "errors",
        "topic_name": "Error Handling",
        "starter_code": '''def safe_int(s, default=0):
    # Parse string to int safely
    pass''',
        "solution": '''def safe_int(s, default=0):
    try:
        return int(s)
    except (ValueError, TypeError):
        return default''',
        "test_cases": [
            {"input": "safe_int('42')", "expected": "42"},
            {"input": "safe_int('abc')", "expected": "0"},
            {"input": "safe_int('xyz', -1)", "expected": "-1"}
        ],
        "estimated_time": 5
    },
    
    # Topic 8: Libraries
    {
        "id": str(uuid.uuid4()),
        "title": "Random Choice",
        "description": "Return a random element from a list using the random module.",
        "difficulty": "easy",
        "topic_slug": "libraries",
        "topic_name": "Libraries & Packages",
        "starter_code": '''import random

def random_choice(items):
    # Return random item
    pass''',
        "solution": '''import random

def random_choice(items):
    return random.choice(items)''',
        "test_cases": [
            {"input": "random_choice([1]) in [1]", "expected": "True"},
            {"input": "random_choice(['a', 'b', 'c']) in ['a', 'b', 'c']", "expected": "True"}
        ],
        "estimated_time": 5
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Math Operations",
        "description": "Calculate the square root and ceiling of a number.",
        "difficulty": "easy",
        "topic_slug": "libraries",
        "topic_name": "Libraries & Packages",
        "starter_code": '''import math

def sqrt_ceil(n):
    # Return ceiling of square root
    pass''',
        "solution": '''import math

def sqrt_ceil(n):
    return math.ceil(math.sqrt(n))''',
        "test_cases": [
            {"input": "sqrt_ceil(16)", "expected": "4"},
            {"input": "sqrt_ceil(17)", "expected": "5"},
            {"input": "sqrt_ceil(2)", "expected": "2"}
        ],
        "estimated_time": 5
    },
]


def get_exercises():
    """Return all exercise data."""
    return EXERCISES
