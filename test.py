from tensorflow.keras.models import load_model



# Path to your saved model

model_path = './myproject/imageapp/New_Test_model.keras'



# Load the trained model

model = load_model(model_path)

print("Model loaded successfully!")

import numpy as np

from tensorflow.keras.preprocessing.image import load_img, img_to_array



# Path to your image

image_path = '25.JPG'



# Load and preprocess the image

img_width, img_height = 224, 224  # Image dimensions

image = load_img(image_path, target_size=(img_width, img_height))  # Load and resize

image_array = img_to_array(image)  # Convert to NumPy array

image_array = image_array / 255.0  # Rescale pixel values

image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension


# Get predictions

predictions = model.predict(image_array)



# Print predictions

print("Predicted probabilities:", predictions)



# Get the class with the highest probability

predicted_class = np.argmax(predictions, axis=1)

print("Predicted class:", predicted_class)



# from tensorflow.keras.models import load_model

# # Load the model
# model = load_model('New_Test_model.keras')

# # Verify the model
# model.summary()