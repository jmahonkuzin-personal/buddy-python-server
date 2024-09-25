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

@app.route('/add_exercise', methods=['POST'])
def add_exercise():
    # Validate input fields
    try:
        data = request.get_json()

        # Extract required field
        exercise_name = data.get('exercise_name')

        # Optional fields (they can be None/NULL)
        weight = data.get('weight')
        weight_unit = data.get('weight_unit')
        sets = data.get('sets')
        reps = data.get('reps')
        workout_time = data.get('workout_time')  # Expect format 'HH:MM:SS'

        # Validate required field
        if not exercise_name:
            return jsonify({'error': 'exercise_name is required'}), 400

        # Optional: Validate the weight_unit if it's provided (otherwise it's skipped)
        if weight_unit and weight_unit not in ['kg', 'lbs']:
            return jsonify({'error': 'Invalid weight unit. Must be "kg" or "lbs".'}), 400

        print("got here")

        # Connect to the database
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Insert data into the exercises table
            insert_query = """
                INSERT INTO exercise (exercise_name, weight, weight_unit, sets, reps, workout_time) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_query, (exercise_name, weight, weight_unit, sets, reps, workout_time))
            conn.commit()

        return jsonify({'message': 'Exercise added successfully!'}), 201

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'error': str(error)}), 500

    finally:
        if conn:
            conn.close()

# GET endpoint to retrieve all data from the exercise table
@app.route('/get_all_exercises', methods=['GET'])
def get_exercises():
    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Execute SQL query to fetch all records from the exercise table
        cur.execute("SELECT * FROM exercise")
        rows = cur.fetchall()

        # Get the column names from the cursor
        column_names = [desc[0] for desc in cur.description]

        exercises = []
        for row in rows:
            row_dict = dict(zip(column_names, row))

            # Format workout_time (timedelta) into a serializable string
            if 'workout_time' in row_dict:
                row_dict['workout_time'] = format_timedelta(row_dict['workout_time'])
            
            exercises.append(row_dict)

        # Convert rows to a list of dictionaries
        # exercises = [dict(zip(column_names, row)) for row in rows]

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Return the data as JSON
        return jsonify(exercises), 200

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'error': str(error)}), 500

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