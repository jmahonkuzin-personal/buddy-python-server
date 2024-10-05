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

@app.route('/add_exercises', methods=['POST'])
def add_exercises():
    try:
        data = request.get_json()
        if not isinstance(exercises_data, list):
            return jsonify({'error': 'Invalid input format, expected a list of exercises'}), 400

        exercises = []
        for item in data:
            exercises.append(get_exercise_from_json(item))

        # Connect to the database
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Insert data into the exercises table
            insert_query = """
                INSERT INTO exercise (exercise_name, weight, weight_unit, sets, reps, workout_time) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.executemany(insert_query, exercises)
            conn.commit()

        return jsonify({'message': 'Exercise list added successfully!'}), 201

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'error': str(error)}), 500

    finally:
        if conn:
            conn.close()
            

@app.route('/add_one_exercise', methods=['POST'])
def add_one_exercise():
    # Validate input fields
    try:
        data = request.get_json()
        exercise = get_exercise_from_json(data)

        # Connect to the database
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Insert data into the exercises table
            insert_query = """
                INSERT INTO exercise (exercise_name, weight, weight_unit, sets, reps, workout_time) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cur.execute(insert_query, exercise)
            conn.commit()

        return jsonify({'message': 'Exercise added successfully!'}), 201

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'error': str(error)}), 500

    finally:
        if conn:
            conn.close()


def get_exercise_from_json(data) {
    # Extract required field
    name = data.get('name')
    exercise_type = data.get('type')

    # Optional fields (they can be None/NULL)
    weight = data.get('weight')
    weight_unit = data.get('weightUnit')
    sets = data.get('sets')
    repsPerSet = data.get('repsPerSet')
    time = data.get('time')  # Expect format 'HH:MM:SS'

    # Validate required field
    if not name, exercise_type:
        return jsonify({'error': 'exercise_name is required'}), 400

    # Optional: Validate the weight_unit if it's provided (otherwise it's skipped)
    if weight_unit and weight_unit not in ['kg', 'lbs']:
        return jsonify({'error': 'Invalid weight unit. Must be "kg" or "lbs".'}), 400

    return (name, weight, weight_unit, sets, repsPerSet, time)
}

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
