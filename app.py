from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import pandas as pd

app = Flask(__name__)

# Konfigurasi JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

# Load Data CSV
data = pd.read_csv('Final_tanah_longsor.csv')

# Data User Dummy
users = {}

# Register
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and Password required"}), 400

    if username in users:
        return jsonify({"msg": "User already exists"}), 400

    users[username] = password
    return jsonify({"msg": "Registration successful"}), 201

# Login
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if users.get(username) != password:
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

# Get All Data
@app.route('/data', methods=['GET'])
@jwt_required()
def get_data():
    return jsonify(data.to_dict(orient='records')), 200

# Get Data by Index
@app.route('/data/<int:index>', methods=['GET'])
@jwt_required()
def get_data_by_index(index):
    if index < 0 or index >= len(data):
        return jsonify({"msg": "Data not found"}), 404

    record = data.iloc[index].to_dict()
    return jsonify(record), 200

# Create New Data
@app.route('/data', methods=['POST'])
@jwt_required()
def create_data():
    global data  # Deklarasi global untuk memodifikasi variabel global
    new_record = request.json

    if not new_record:
        return jsonify({"msg": "Invalid data"}), 400

    if not set(['Fasilitas Kesehatan', 'Fasilitas Pendidikan', 'Provinsi', 'Tahun', 'Jumlah Kejadian']).issubset(new_record.keys()):
        return jsonify({"msg": "Missing fields in request body"}), 400

    data = pd.concat([data, pd.DataFrame([new_record])], ignore_index=True)
    return jsonify({"msg": "Data created successfully"}), 201

# Update Data by Index
@app.route('/data/<int:index>', methods=['PUT'])
@jwt_required()
def update_data(index):
    global data  # Deklarasi global untuk memodifikasi variabel global
    if index < 0 or index >= len(data):
        return jsonify({"msg": "Data not found"}), 404

    updated_record = request.json
    if not updated_record:
        return jsonify({"msg": "Invalid data"}), 400

    for key, value in updated_record.items():
        if key in data.columns:
            data.at[index, key] = value

    return jsonify({"msg": "Data updated successfully"}), 200

# Delete Data by Index
@app.route('/data/<int:index>', methods=['DELETE'])
@jwt_required()
def delete_data(index):
    global data  # Deklarasi global untuk memodifikasi variabel global
    if index < 0 or index >= len(data):
        return jsonify({"msg": "Data not found"}), 404

    data = data.drop(index).reset_index(drop=True)
    return jsonify({"msg": "Data deleted successfully"}), 200

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
