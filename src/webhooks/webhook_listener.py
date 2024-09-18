from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.get_json
        print(f"Received request: {data}")

        return jsonify({'message': 'Webhook received successfully!'}), 200
    return jsonify({'message': 'Webhook not received!'}), 405


if __name__ == '__main__':
    app.run(port=5000)
