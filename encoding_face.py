import face_recognition
import numpy as np

# Load the image file
image_path = "test-face.jpg"
image = face_recognition.load_image_file(image_path)

# Find all face locations in the image
face_locations = face_recognition.face_locations(image)

# If no faces are found, return an empty list
if len(face_locations) == 0:
    print("No faces found in the image.")
    user_face_encoding = []
else:
    # Assume there's only one face in the image
    # Get the face encoding for the first face
    face_encoding = face_recognition.face_encodings(image, face_locations)[0]

    # Convert the face encoding numpy array to a regular list
    user_face_encoding = face_encoding.tolist()

# Print the extracted face encoding
print(user_face_encoding)
