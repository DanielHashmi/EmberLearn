"""
EmberLearn Demo Backend - No dependencies required
Run with: python3 demo_server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class EmberLearnHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        if self.path == '/health':
            self._set_headers()
            response = {"status": "healthy", "service": "emberlearn_demo"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/topics':
            self._set_headers()
            response = {
                "topics": [
                    {"id": "basics", "name": "Python Basics", "completed": 5, "total": 10},
                    {"id": "loops", "name": "Loops & Control Flow", "completed": 3, "total": 8},
                    {"id": "functions", "name": "Functions", "completed": 0, "total": 12},
                ]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'

        try:
            data = json.loads(body)
        except:
            data = {}

        query = data.get('query', data.get('message', ''))

        if self.path == '/api/chat':
            self._set_headers()

            # Smart routing based on query
            if any(word in query.lower() for word in ['loop', 'for', 'while', 'iterate']):
                response_text = """**Python Loops Explained:**

There are two main types of loops in Python:

1. **For Loops** - Iterate over sequences:
```python
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4

fruits = ['apple', 'banana', 'cherry']
for fruit in fruits:
    print(fruit)
```

2. **While Loops** - Run while condition is true:
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

**Key Concepts:**
- `break` - Exit the loop early
- `continue` - Skip to next iteration
- `range(n)` - Generate numbers 0 to n-1

Would you like to try a coding exercise on loops?"""

            elif any(word in query.lower() for word in ['function', 'def', 'return']):
                response_text = """**Python Functions Explained:**

Functions are reusable blocks of code:

```python
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")  # Returns "Hello, Alice!"
```

**Key Concepts:**
- Define with `def` keyword
- Parameters in parentheses
- `return` sends value back
- Can have default parameters:

```python
def power(base, exponent=2):
    return base ** exponent

power(3)     # Returns 9 (3^2)
power(3, 3)  # Returns 27 (3^3)
```

**Best Practices:**
- Use descriptive names
- One function = one task
- Add docstrings for documentation

Try writing your own function!"""

            elif any(word in query.lower() for word in ['error', 'bug', 'debug', 'fix']):
                response_text = """**Debugging Python Code:**

Let me help you debug! Common Python errors:

1. **SyntaxError** - Check for:
   - Missing colons `:` after if/for/def
   - Unclosed parentheses or quotes
   - Wrong indentation

2. **NameError** - Variable not defined:
   ```python
   # ❌ print(x)  # Error if x not defined
   # ✅ x = 5; print(x)
   ```

3. **TypeError** - Wrong data type:
   ```python
   # ❌ "5" + 5  # Can't add string and int
   # ✅ int("5") + 5  # Convert first
   ```

**Debugging Tips:**
- Use `print()` statements to check values
- Read error messages carefully (bottom line first)
- Check line numbers in traceback

Share your error message and I'll help identify the issue!"""

            elif any(word in query.lower() for word in ['exercise', 'practice', 'challenge', 'problem']):
                response_text = """**Coding Exercise: FizzBuzz Challenge**

Write a function that prints numbers 1 to 100, but:
- For multiples of 3, print "Fizz"
- For multiples of 5, print "Buzz"
- For multiples of both 3 and 5, print "FizzBuzz"

**Example Output:**
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
...
```

**Hints:**
- Use a `for` loop with `range(1, 101)`
- Check divisibility with modulo operator `%`
- Check multiples of 15 first!

Try coding this and I'll review your solution!"""

            elif any(word in query.lower() for word in ['progress', 'score', 'mastery']):
                response_text = """**Your Learning Progress:**

📊 **Overall Mastery: 68%** (Learning Level)

**Topic Breakdown:**
- ✅ Python Basics: 85% (Proficient)
- 🟡 Loops: 65% (Learning)
- 🔴 Functions: 45% (Beginner)
- ⚪ OOP: 10% (Just Started)

**This Week:**
- 12 exercises completed
- 5-day streak! 🔥
- 4 concepts mastered

**Next Steps:**
1. Complete 3 more loop exercises to reach 70%
2. Start function parameters lesson
3. Take the mid-module quiz

Keep up the great work! 🎉"""

            else:
                response_text = f"""**EmberLearn AI Tutor**

I'm here to help you master Python! I can help with:

🎓 **Learn Concepts** - Explain Python topics with examples
📝 **Review Code** - Analyze your code for improvements
🐛 **Debug Errors** - Help fix bugs and understand errors
💪 **Practice** - Generate coding exercises
📊 **Track Progress** - Monitor your learning journey

You asked: "{query}"

This is a **demo version**. For full AI-powered responses:
1. Set your OPENAI_API_KEY in backend/.env
2. Run: python3 backend/simple_triage_server.py

**Try asking:**
- "How do for loops work?"
- "Debug my code"
- "Give me an exercise"
- "Show my progress"
"""

            response = {
                "response": response_text,
                "agent": "demo",
                "timestamp": "2026-01-06T13:00:00Z"
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/api/execute':
            self._set_headers()
            code = data.get('code', '')

            # Simple safe execution simulation
            if 'print' in code and 'Hello' in code:
                output = "Hello, World!\n"
            elif 'range(5)' in code:
                output = "0\n1\n2\n3\n4\n"
            else:
                output = "Code executed successfully!\n(Set OPENAI_API_KEY for real execution)"

            response = {
                "output": output,
                "status": "success",
                "execution_time": "0.05s"
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/api/auth/login':
            self._set_headers()
            response = {
                "token": "demo_token_12345",
                "user": {
                    "id": "demo_user",
                    "name": "Demo Student",
                    "email": data.get('email', 'demo@emberlearn.com')
                }
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/api/auth/register':
            self._set_headers()
            response = {
                "token": "demo_token_12345",
                "user": {
                    "id": "demo_user",
                    "name": data.get('name', 'New Student'),
                    "email": data.get('email', 'student@emberlearn.com')
                }
            }
            self.wfile.write(json.dumps(response).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, EmberLearnHandler)
    print(f"""
╔══════════════════════════════════════════════════════╗
║          🚀 EmberLearn Backend Running!              ║
╚══════════════════════════════════════════════════════╝

✅ Server:  http://localhost:{port}
✅ Health:  http://localhost:{port}/health
✅ Topics:  http://localhost:{port}/api/topics
✅ Chat:    POST http://localhost:{port}/api/chat

📖 Open http://localhost:3000 in your browser
💬 Start chatting with the AI tutor!

⚡ Running in DEMO mode (no dependencies required)
   For full AI: Set OPENAI_API_KEY and use simple_triage_server.py

Press Ctrl+C to stop
""")
    httpd.serve_forever()

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
