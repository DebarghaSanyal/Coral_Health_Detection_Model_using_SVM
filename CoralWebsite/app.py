from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from PIL import Image
import numpy as np
import joblib

app = Flask(__name__)
CORS(app)  # Keep for flexibility

vgg_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
svm = joblib.load('svm_model.pkl')
scaler = joblib.load('scaler.pkl')

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

def preprocess_single_image(image):
    img = Image.open(image).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = preprocess_input(img_array)
    return np.expand_dims(img_array, axis=0)

def predict_single_image(image, vgg_model, svm, scaler):
    img_batch = preprocess_single_image(image)
    if img_batch is None:
        return None, None
    features = vgg_model.predict(img_batch)
    features = features.reshape(features.shape[0], -1)
    features = scaler.transform(features)
    prediction = svm.predict(features)
    confidence = svm.decision_function(features)
    # print("confidence:", confidence)  # Debug print
    healthy_percentage = (1 / (1 + np.exp(confidence))) * 100   # Convert to percentage 
    # healthy_percentage = (1 / (1 + np.exp(-confidence))) * 100  # Convert to percentage
    # print("Healthy Percentage:", healthy_percentage)  # Debug print
    return ("Healthy Coral" if prediction[0] == 0 else "Bleached Coral", healthy_percentage[0])

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    image = request.files['image']
    result, healthy_percentage = predict_single_image(image, vgg_model, svm, scaler)
    if result is None:
        return jsonify({'error': 'Error processing image'}), 500
    return jsonify({'prediction': result, 'healthy_percentage': healthy_percentage})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)