from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/servicebus", methods=['POST'])
def incoming():
    data=request.get_json()
    print("Received json message from ServiceBus!")
    print(data , flush=True)
    return "ServiceBus Event Processed!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
