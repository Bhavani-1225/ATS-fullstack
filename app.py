from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_pymongo import PyMongo
import os
import logging

app = Flask(__name__)

# Configure MongoDB URI (using your MongoDB Atlas connection string)
app.config['MONGO_URI'] = 'mongodb+srv://ramya:BsvPSIBAuaiWVdMS@cluster0.8fjqm.mongodb.net/flask_app?retryWrites=true&w=majority'
mongo = PyMongo(app)

# Configure file upload settings
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route for handling job application
@app.route('/apply-job', methods=['POST'])
def apply_job():
    try:
        email = request.form.get('email')
        job_id = request.form.get('job_id')
        file = request.files.get('resume')

        if not email or not job_id or not file:
            return jsonify({"error": "All fields are required."}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Save application data to MongoDB
            application = {
                "email": email,
                "job_id": job_id,
                "resume": file_path
            }
            mongo.db.applications.insert_one(application)

            return jsonify({"message": "Job application submitted successfully!"}), 201
        else:
            return jsonify({"error": "Invalid file type. Please upload a PDF or Word document."}), 400
    except Exception as e:
        # Log the error for debugging purposes
        app.logger.error(f"Error while processing job application: {str(e)}")
        return jsonify({"error": "An error occurred while processing your application."}), 500

if __name__ == '__main__':
    # Enable logging for the application
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
