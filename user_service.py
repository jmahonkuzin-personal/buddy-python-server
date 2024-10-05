from flask import Flask, request, jsonify
import psycopg2
import os
from datetime import timedelta

app = Flask(__name__)

# Database connection details
DB_HOST = "third-place-trivia-1877.jxf.gcp-us-east1.cockroachlabs.cloud"
DB_PORT = 26257  # Default port for CockroachDB
DB_USER = "julia-mahonkuzin"
DB_PASSWORD = "LWK6vatlCGW8_mIVaugoaQ"
DB_NAME = "workoutbuddy"


@app.route('/test_connection', methods=['GET'])
def test_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"message": "Database connection successful!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/echo', methods=['POST'])
def echo():
    data = request.json
    if 'message' not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data['message']
    return jsonify({"received": message}), 200


@app.route('/verify_user', methods=['POST'])
def verify_user():
    data = request.json
    if 'username' or 'password' not in data:
        return jsonify({"error": "Missing required field(s), 'username' or 'password'"}), 400

    username = data['username']
    password = data['password']

    return jsonify({"received": username+password}), 200


def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        sslmode='require'  # Enable SSL
    )
    return conn

# Helper function to format timedelta into a string
def format_timedelta(td):
    if isinstance(td, timedelta):
        # Format timedelta to HH:MM:SS string
        return str(td)
    return td

if __name__ == '__main__':
    app.run(debug=True)