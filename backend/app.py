from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# -----------------------------
# RDS CONFIGURATION
# -----------------------------
DB_CONFIG = {
    "host": "database-1.cheya44kugwh.ap-southeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": "Sz007*321*",
    "database": "Testapp",
    "port": 3306
}

# -----------------------------
# DB CONNECTION
# -----------------------------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "Flask API is running"
    })

# -----------------------------
# GET PERSON API
# -----------------------------
@app.route("/api/person/<name>", methods=["GET"])
def get_person(name):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT name, designation, email, location
            FROM persons
            WHERE name = %s
        """

        cursor.execute(query, (name,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:
            return jsonify({
                "status": "error",
                "message": "Person not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": {
                "name": row[0],
                "designation": row[1],
                "email": row[2],
                "location": row[3]
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Database error",
            "details": str(e)
        }), 500


# -----------------------------
# RUN APP (DEV ONLY)
# -----------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
