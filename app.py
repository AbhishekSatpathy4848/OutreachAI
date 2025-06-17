from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def home():
    print(request.json)
    return 'Data received', 200

@app.route('/', methods=['GET'])
def health_check():
    return 'Running...', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)