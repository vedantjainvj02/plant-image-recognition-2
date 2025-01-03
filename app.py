from flask import Flask, render_template, request, redirect, url_for
import os
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Load the pre-trained model
model = MobileNetV2(weights='imagenet')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if the image is part of the request
    if 'image' not in request.files:
        return 'No image part in the request', 400
    img_file = request.files['image']
    # If no file is selected
    if img_file.filename == '':
        return 'No image selected', 400
    if img_file:
        # Save the image to the upload folder
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], img_file.filename)
        img_file.save(image_path)
        # Process the image and recognize the obj
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_batch = np.expand_dims(img_array, axis=0)
        img_preprocessed = preprocess_input(img_batch)
        predictions = model.predict(img_preprocessed)
        # Decode the predictions
        decoded_predictions = decode_predictions(predictions, top=3)[0]
        # Get the top prediction
        obj_name = decoded_predictions[0][1]
        obj_name = str(obj_name).replace('_', ' ').capitalize()
        obj_info = f"Confidence: {decoded_predictions[0][2]*100:.2f}%"
        # Render the result template with the recognized obj's name and information
        return render_template('result.html', obj_name=obj_name, obj_info=obj_info, obj_image=image_path)
    else:
        return 'Unsupported file type', 400

if __name__ == '__main__':
    app.run(debug=True)