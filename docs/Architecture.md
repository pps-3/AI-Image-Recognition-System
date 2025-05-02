# AI Vision Lab: System Architecture Documentation

## Overview

This document explains the architecture and data flow of the AI Vision Lab image recognition system, focusing on how the Flask backend (app.py) interacts with the frontend interface.

## System Architecture

```
┌─────────────────┐      HTTP Requests      ┌─────────────────┐      ┌─────────────────┐
│                 │ ───────────────────────> │                 │ ───> │                 │
│     Frontend    │                          │  Flask Backend  │      │    MongoDB      │
│    (index.html) │ <───────────────────────┐│    (app.py)    │ <─── │    Database     │
│                 │      JSON Responses      │                 │      │                 │
└─────────────────┘                          └─────────────────┘      └─────────────────┘
                                                     │
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │   TensorFlow    │
                                            │   MobileNetV2   │
                                            │      Model      │
                                            └─────────────────┘
```

## Components

### 1. Frontend (index.html)

The frontend is a single-page HTML application with JavaScript that provides:

- User interface for image upload (drag & drop or file selection)
- Image preview functionality
- Results display with primary and alternative predictions
- Dark/light mode toggle
- Team credits section

### 2. Flask Backend (app.py)

The Flask backend serves as both an API server and static file server:

- Handles image uploads and preprocessing
- Communicates with the TensorFlow model for predictions
- Stores results in MongoDB
- Serves the frontend static files

### 3. TensorFlow Model

- Pre-trained MobileNetV2 model for image classification
- Provides predictions with confidence scores

### 4. MongoDB Database

- Stores uploaded images (as base64) and prediction results
- Enables retrieval of past predictions

## Data Flow

### Image Upload and Prediction Process

```
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│  User     │     │  Frontend │     │  Flask    │     │ TensorFlow│     │  MongoDB  │
│  Action   │     │  (JS)     │     │  Backend  │     │  Model    │     │  Database │
└─────┬─────┘     └─────┬─────┘     └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
      │                 │                 │                 │                 │
      │ Upload Image    │                 │                 │                 │
      │────────────────>│                 │                 │                 │
      │                 │                 │                 │                 │
      │                 │ POST /predict   │                 │                 │
      │                 │────────────────>│                 │                 │
      │                 │                 │                 │                 │
      │                 │                 │ Preprocess Image│                 │
      │                 │                 │─────────────────>                 │
      │                 │                 │                 │                 │
      │                 │                 │                 │ Return          │
      │                 │                 │                 │ Predictions     │
      │                 │                 │ <───────────────│                 │
      │                 │                 │                 │                 │
      │                 │                 │ Store Result    │                 │
      │                 │                 │────────────────────────────────────>
      │                 │                 │                 │                 │
      │                 │ JSON Response   │                 │                 │
      │                 │ <───────────────│                 │                 │
      │                 │                 │                 │                 │
      │ Display Results │                 │                 │                 │
      │ <───────────────│                 │                 │                 │
      │                 │                 │                 │                 │
```

## Key API Endpoints

### 1. `/` (GET)

Serves the main frontend interface (index.html).

```python
@app.route("/")
def index():
    return render_template("index.html")
```

### 2. `/predict` (POST)

Handles image uploads and returns prediction results.

```python
@app.route("/predict", methods=["POST"])
def predict():
    # Process uploaded image
    # Get predictions from model
    # Store in MongoDB
    # Return JSON response
```

### 3. `/get-image/<filename>` (GET)

Retrieves previously uploaded images from MongoDB.

```python
@app.route("/get-image/<filename>", methods=["GET"])
def get_image(filename):
    # Retrieve image from MongoDB
    # Return image file
```

## Code Breakdown: app.py

### Imports and Setup

```python
from flask import Flask, request, jsonify, render_template, send_file
import tensorflow as tf
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import base64
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["mydb"]
collection = db["images"]

# Flask app initialization with static folder configuration
app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

# Load TensorFlow model
model = tf.keras.applications.MobileNetV2(weights="imagenet")
```

### Image Preprocessing

```python
def preprocess_image(image):
    """Preprocess the image for MobileNetV2"""
    # Convert image to RGB if needed
    if image.mode == "RGBA":
        image = image.convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")

    # Resize to required dimensions
    image = image.resize((224, 224))
    
    # Normalize pixel values
    image = np.array(image) / 255.0
    
    # Add batch dimension
    image = np.expand_dims(image, axis=0)
    return image
```

### Prediction Endpoint

```python
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get uploaded image
        file = request.files["image"]
        image = Image.open(io.BytesIO(file.read()))

        # Preprocess image
        processed_image = preprocess_image(image)

        # Get predictions from model
        predictions = model.predict(processed_image)
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]
        
        # Extract top prediction and alternatives
        top_prediction = decoded_predictions[0]
        label = top_prediction[1]
        confidence = float(top_prediction[2])
        
        all_predictions = [
            {"label": pred[1], "confidence": float(pred[2])} 
            for pred in decoded_predictions
        ]

        # Store in MongoDB
        file.seek(0)
        encoded_image = base64.b64encode(file.read()).decode()

        image_data = {
            "filename": file.filename,
            "image": encoded_image,
            "label": label,
            "confidence": confidence,
            "all_predictions": all_predictions
        }
        collection.insert_one(image_data)

        # Return JSON response
        return jsonify({
            "label": label, 
            "confidence": confidence,
            "all_predictions": all_predictions,
            "message": "Image and prediction stored in MongoDB!"
        })

    except Exception as e:
        return jsonify({"error": "Error processing image", "details": str(e)}), 500
```

## Frontend-Backend Integration

The frontend JavaScript communicates with the Flask backend through fetch API calls:

```javascript
async function analyzeImage() {
    if (!selectedFile) return;
    
    // Show loading state
    loading.style.display = 'block';
    resultsPlaceholder.style.display = 'none';
    resultsContainer.style.display = 'none';
    
    // Prepare form data with the image
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    try {
        // Send to backend
        const response = await fetch('http://127.0.0.1:5001/predict', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze image');
        }
        
        // Parse the JSON response
        const data = await response.json();
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Something went wrong. Please try again.');
        loading.style.display = 'none';
        resultsPlaceholder.style.display = 'block';
    }
}
```

## Deployment Considerations

1. **Production Server**: In production, use a WSGI server like Gunicorn instead of Flask's development server
2. **Environment Variables**: Store sensitive information like database credentials in environment variables
3. **Error Handling**: Implement more robust error handling and logging
4. **Security**: Add authentication for API endpoints in a production environment
5. **Scaling**: Consider containerization with Docker for easier deployment and scaling

## Conclusion

The AI Vision Lab system demonstrates a clean architecture with clear separation of concerns:

- Frontend handles user interaction and result display
- Backend manages image processing, AI model integration, and data storage
- MongoDB provides persistence for images and predictions
- TensorFlow delivers the AI capabilities through a pre-trained model

This architecture is modular and extensible, allowing for future enhancements such as user accounts, additional AI models, or more advanced image processing capabilities.
