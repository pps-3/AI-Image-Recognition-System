from flask import Flask, request, jsonify, render_template, send_file
import tensorflow as tf
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import base64
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mydb"]
collection = db["images"]

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
# Enable CORS for all routes with additional options
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

model = tf.keras.applications.MobileNetV2(weights="imagenet")

def preprocess_image(image):
    """Preprocess the image for MobileNetV2"""
    if image.mode == "RGBA":
        image = image.convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")

    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["image"]
        image = Image.open(io.BytesIO(file.read()))

        processed_image = preprocess_image(image)

        predictions = model.predict(processed_image)
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]
        
        # Get primary prediction
        top_prediction = decoded_predictions[0]
        label = top_prediction[1]
        confidence = float(top_prediction[2])
        
        # Get all top 3 predictions for more comprehensive results
        all_predictions = [
            {"label": pred[1], "confidence": float(pred[2])} 
            for pred in decoded_predictions
        ]

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

        return jsonify({
            "label": label, 
            "confidence": confidence,
            "all_predictions": all_predictions,
            "message": "Image and prediction stored in MongoDB!"
        })

    except Exception as e:
        return jsonify({"error": "Error processing image", "details": str(e)}), 500

@app.route("/get-image/<filename>", methods=["GET"])
def get_image(filename):
    result = collection.find_one({"filename": filename})
    if not result:
        return jsonify({"error": "File not found"}), 404

    # Convert base64 back to bytes
    image_data = base64.b64decode(result["image"])
    image_bytes = io.BytesIO(image_data)
    image_bytes.seek(0)
    # Use send_file to return the image
    return send_file(image_bytes, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
