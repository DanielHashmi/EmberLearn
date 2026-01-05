"""
Fallback Responses - Cached responses for common queries when OpenAI API is unavailable.
Provides graceful degradation for the tutoring system.
"""

from typing import Optional
import structlog

logger = structlog.get_logger()


# Cached responses for common Python topics
FALLBACK_RESPONSES = {
    # Variables and Data Types
    "variables": {
        "explanation": """Variables in Python are containers for storing data values. Unlike other programming languages, Python has no command for declaring a variable - you create one the moment you assign a value to it.

**Creating Variables:**
```python
x = 5           # integer
name = "Alice"  # string
pi = 3.14       # float
is_valid = True # boolean
```

**Key Points:**
- Variable names are case-sensitive (age and Age are different)
- Must start with a letter or underscore
- Can only contain alphanumeric characters and underscores
- Cannot be Python keywords (like `if`, `for`, `class`)""",
        "examples": [
            "x = 10",
            "name = 'Python'",
            "numbers = [1, 2, 3]",
        ],
    },
    # Control Flow
    "if": {
        "explanation": """If statements in Python allow you to execute code conditionally based on whether an expression evaluates to True or False.

**Basic Syntax:**
```python
if condition:
    # code to execute if condition is True
elif another_condition:
    # code if first condition is False but this is True
else:
    # code if all conditions are False
```

**Key Points:**
- Indentation is crucial - Python uses it to define code blocks
- Conditions can use comparison operators: ==, !=, <, >, <=, >=
- Logical operators: and, or, not""",
        "examples": [
            "if x > 0:\n    print('Positive')",
            "if age >= 18:\n    print('Adult')\nelse:\n    print('Minor')",
        ],
    },
    # Loops
    "for": {
        "explanation": """For loops in Python iterate over a sequence (list, tuple, string, or range).

**Basic Syntax:**
```python
for item in sequence:
    # code to execute for each item
```

**Common Patterns:**
```python
# Iterate over a range
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# Iterate over a list
fruits = ['apple', 'banana', 'cherry']
for fruit in fruits:
    print(fruit)

# Iterate with index
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```""",
        "examples": [
            "for i in range(10):\n    print(i)",
            "for char in 'hello':\n    print(char)",
        ],
    },
    "while": {
        "explanation": """While loops execute a block of code as long as a condition is True.

**Basic Syntax:**
```python
while condition:
    # code to execute while condition is True
```

**Important:** Make sure the condition eventually becomes False, or you'll have an infinite loop!

**Example:**
```python
count = 0
while count < 5:
    print(count)
    count += 1  # Don't forget to update!
```""",
        "examples": [
            "while x > 0:\n    x -= 1",
            "while True:\n    if done:\n        break",
        ],
    },
    # Functions
    "functions": {
        "explanation": """Functions are reusable blocks of code that perform a specific task.

**Defining a Function:**
```python
def function_name(parameters):
    # code block
    return result  # optional
```

**Example:**
```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Alice")  # "Hello, Alice!"
```

**Key Concepts:**
- Parameters: Variables listed in the function definition
- Arguments: Values passed when calling the function
- Return: Sends a value back to the caller
- Default parameters: `def greet(name="World")`""",
        "examples": [
            "def add(a, b):\n    return a + b",
            "def greet(name='World'):\n    print(f'Hello, {name}!')",
        ],
    },
    # Lists
    "lists": {
        "explanation": """Lists are ordered, mutable collections that can hold items of different types.

**Creating Lists:**
```python
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]
empty = []
```

**Common Operations:**
```python
# Access by index (0-based)
first = numbers[0]  # 1
last = numbers[-1]  # 5

# Slicing
subset = numbers[1:3]  # [2, 3]

# Modify
numbers.append(6)      # Add to end
numbers.insert(0, 0)   # Insert at index
numbers.remove(3)      # Remove first occurrence
popped = numbers.pop() # Remove and return last
```""",
        "examples": [
            "my_list = [1, 2, 3]",
            "my_list.append(4)",
            "for item in my_list:\n    print(item)",
        ],
    },
    # Dictionaries
    "dictionaries": {
        "explanation": """Dictionaries store key-value pairs, allowing fast lookup by key.

**Creating Dictionaries:**
```python
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}
```

**Common Operations:**
```python
# Access values
name = person["name"]  # "Alice"
age = person.get("age", 0)  # 30 (with default)

# Modify
person["email"] = "alice@example.com"  # Add/update
del person["city"]  # Remove

# Iterate
for key, value in person.items():
    print(f"{key}: {value}")
```""",
        "examples": [
            "my_dict = {'a': 1, 'b': 2}",
            "value = my_dict.get('a')",
            "my_dict['c'] = 3",
        ],
    },
    # Classes
    "classes": {
        "explanation": """Classes are blueprints for creating objects with attributes and methods.

**Basic Class:**
```python
class Dog:
    def __init__(self, name, age):
        self.name = name  # instance attribute
        self.age = age

    def bark(self):  # method
        return f"{self.name} says woof!"

# Create an instance
my_dog = Dog("Buddy", 3)
print(my_dog.bark())  # "Buddy says woof!"
```

**Key Concepts:**
- `__init__`: Constructor method, called when creating an instance
- `self`: Reference to the current instance
- Attributes: Variables belonging to an object
- Methods: Functions belonging to a class""",
        "examples": [
            "class Person:\n    def __init__(self, name):\n        self.name = name",
            "obj = MyClass()",
        ],
    },
}

# Common error explanations
ERROR_EXPLANATIONS = {
    "NameError": "This error occurs when you try to use a variable that hasn't been defined yet. Check for typos in variable names or make sure you've assigned a value before using it.",
    "TypeError": "This error happens when you try to perform an operation on incompatible types. For example, adding a string to an integer without conversion.",
    "SyntaxError": "This means Python couldn't understand your code structure. Check for missing colons, parentheses, or incorrect indentation.",
    "IndentationError": "Python uses indentation to define code blocks. Make sure your code is consistently indented (use 4 spaces per level).",
    "IndexError": "You tried to access an index that doesn't exist in a list or string. Remember, indices start at 0!",
    "KeyError": "You tried to access a dictionary key that doesn't exist. Use .get() method for safer access.",
    "ValueError": "The value you provided is the right type but inappropriate. For example, int('hello') fails because 'hello' isn't a valid number.",
    "AttributeError": "You tried to access an attribute or method that doesn't exist on the object. Check the object's type and available methods.",
    "ZeroDivisionError": "You tried to divide by zero, which is mathematically undefined. Add a check before dividing.",
}


def get_fallback_response(topic: str) -> Optional[dict]:
    """Get a cached response for a topic."""
    topic_lower = topic.lower().strip()

    # Direct match
    if topic_lower in FALLBACK_RESPONSES:
        return FALLBACK_RESPONSES[topic_lower]

    # Partial match
    for key, response in FALLBACK_RESPONSES.items():
        if key in topic_lower or topic_lower in key:
            return response

    return None


def get_error_explanation(error_type: str) -> Optional[str]:
    """Get explanation for a Python error type."""
    for key, explanation in ERROR_EXPLANATIONS.items():
        if key.lower() in error_type.lower():
            return explanation
    return None


def get_fallback_for_query(query: str) -> Optional[str]:
    """
    Attempt to provide a fallback response for a query when API is unavailable.
    """
    query_lower = query.lower()

    # Check for topic keywords
    for topic, response in FALLBACK_RESPONSES.items():
        if topic in query_lower:
            logger.info("fallback_response_used", topic=topic)
            return response["explanation"]

    # Check for error keywords
    for error_type in ERROR_EXPLANATIONS:
        if error_type.lower() in query_lower:
            logger.info("fallback_error_explanation_used", error_type=error_type)
            return ERROR_EXPLANATIONS[error_type]

    # Generic fallback
    return """I'm currently unable to connect to the AI service. Here are some resources that might help:

1. **Python Documentation**: https://docs.python.org/3/
2. **Python Tutorial**: https://docs.python.org/3/tutorial/
3. **Common Topics**: Try asking about variables, loops, functions, lists, or dictionaries

Please try again in a few moments, or check your specific topic in the documentation."""
