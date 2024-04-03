import json
from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Replace with your actual MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "input_fields"

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'  # Define an upload folder

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/uploadPickle', methods=['POST'])
def upload_pickle():
    
    if 'pickleFile' not in request.files:
        return jsonify({'error': 'No pickle file uploaded'}), 404

    pickle_file = request.files['pickleFile']
    title = request.form.get('title')
    description = request.form.get('description')

    print(pickle_file.mimetype)

    if pickle_file.filename == '':
        return jsonify({'error': 'No selected file'}), 404

    # if not pickle_file.mimetype.endswith('pkl'):
    #     return jsonify({'error': 'Invalid file format. Only pickle files allowed'}), 404

    # Generate a unique filename to avoid conflicts
    filename = f"{pickle_file.filename}_{os.urandom(10).hex()}.pkl"
    saved_path = os.path.join(UPLOAD_FOLDER, filename)
    model_name = request.form.get('modelName')
    try:
        # Connect to MongoDB
        inputs = json.loads(request.form.get('inputs'))
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db["models"]
        data = {
            "modelName": model_name,
            "inputs": inputs
        }
        collection.insert_one(data)
        client.close()
        pickle_file.save(saved_path)

        # Save additional information (title, description) to a separate file (optional)
        info_path = os.path.join(UPLOAD_FOLDER, f"{filename}.info")
        with open(info_path, 'w') as info_file:
            info_file.write(f"Title: {title}\n")
            info_file.write(f"Description: {description}\n")

        return jsonify({'message': 'Pickle file uploaded successfully!'}), 200
    except Exception as e:
        return jsonify({'error': f"Error uploading file: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
