from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Math Operations API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .operation { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
                .try-it { margin-top: 20px; }
                input, button { padding: 8px; margin: 5px; }
                #result { margin-top: 10px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Math Operations API</h1>
            <p>This API performs basic math operations. Try it out!</p>
            
            <div class="operation">
                <h2>Addition</h2>
                <p>Endpoint: <code>/api/add?a=5&b=3</code></p>
                <p>Example response: <pre>{"result": 8}</pre></p>
            </div>
            
            <div class="operation">
                <h2>Subtraction</h2>
                <p>Endpoint: <code>/api/subtract?a=5&b=3</code></p>
                <p>Example response: <pre>{"result": 2}</pre></p>
            </div>
            
            <div class="operation">
                <h2>Multiplication</h2>
                <p>Endpoint: <code>/api/multiply?a=5&b=3</code></p>
                <p>Example response: <pre>{"result": 15}</pre></p>
            </div>
            
            <div class="operation">
                <h2>Division</h2>
                <p>Endpoint: <code>/api/divide?a=6&b=3</code></p>
                <p>Example response: <pre>{"result": 2.0}</pre></p>
                <p>Note: Division by zero will return an error: <pre>{"error": "Cannot divide by zero"}</pre></p>
            </div>
            
            <div class="try-it">
                <h2>Try it out:</h2>
                <select id="operation">
                    <option value="add">Addition</option>
                    <option value="subtract">Subtraction</option>
                    <option value="multiply">Multiplication</option>
                    <option value="divide">Division</option>
                </select>
                <input type="number" id="num1" placeholder="First number" value="10">
                <input type="number" id="num2" placeholder="Second number" value="2">
                <button onclick="calculate()">Calculate</button>
                <div id="result"></div>
            </div>
            
            <script>
                function calculate() {
                    const operation = document.getElementById('operation').value;
                    const a = document.getElementById('num1').value;
                    const b = document.getElementById('num2').value;
                    
                    fetch(`/api/${operation}?a=${a}&b=${b}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                document.getElementById('result').innerText = `Error: ${data.error}`;
                            } else {
                                document.getElementById('result').innerText = `Result: ${data.result}`;
                            }
                        })
                        .catch(error => {
                            document.getElementById('result').innerText = `Error: ${error.message}`;
                        });
                }
            </script>
        </body>
    </html>
    """

@app.route('/api/add')
def add():
    a = float(request.args.get('a', 0))
    b = float(request.args.get('b', 0))
    return jsonify({"result": a + b})

@app.route('/api/subtract')
def subtract():
    a = float(request.args.get('a', 0))
    b = float(request.args.get('b', 0))
    return jsonify({"result": a - b})

@app.route('/api/multiply')
def multiply():
    a = float(request.args.get('a', 0))
    b = float(request.args.get('b', 0))
    return jsonify({"result": a * b})

@app.route('/api/divide')
def divide():
    a = float(request.args.get('a', 0))
    b = float(request.args.get('b', 0))
    
    # Fixed version with proper error handling for division by zero
    if b == 0:
        return jsonify({"error": "Cannot divide by zero"}), 400
    
    return jsonify({"result": a / b})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
