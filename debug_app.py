from flask import jsonify, Flask, request
appFlask = Flask(__name__)

@appFlask.route('/home')
def home():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if auth == 'SUPPER_EMAIL':
        result = jsonify(deviceList=["1","2"]), 200
    else:
        result = jsonify({"message": "ERROR: Unauthorized"}), 401

    return result
if __name__ == "__main__":
    appFlask.run(host="0.0.0.0", port=5001)