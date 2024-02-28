import base64
import face_recognition
import asyncio
import websockets
import json, io
import requests


baseUrl = 'http://10.17.24.1:8080'

# Dictionary to store user face encodings
user_face_encodings = {}
user_ids = []

expected_fields = ["Authorization", "fcmToken", "refreshToken", "lang"]

async def websocket_handler(websocket, path):
    try:
        user_id = id(websocket)
        print("user_id")
        print(user_id)
        async for message in websocket:

            # Decode the received JSON message
            data = json.loads(message)
            if all(field in data for field in expected_fields):

                if user_id in user_ids:
                    # Decode the base64-encoded image data
                    base64_image = data["image"]
                    image_bytes = base64.b64decode(base64_image)
                    # Process the image using face_recognition
                    response = recognize_face(image_bytes, websocket)
                    print(response)
                    await websocket.send(json.dumps(response))
                    
                else:
                     bodyData = {
                         'refreshToken': data["refreshToken"],
                         'fcmToken': data["fcmToken"],
                         'lang': data["lang"]
                         }
                
                     headers = {
                           'Authorization': data["Authorization"],
                           'Accept-Language': data["lang"],
                           'Content-type': 'application/json',
                          'Accept': 'application/json'
                          }
                
                     print(f'{baseUrl}/refreshToken')
                     apiResponse = requests.post(f'{baseUrl}/refreshToken', json = bodyData, headers = headers)
                     print(apiResponse.status_code)
                     if apiResponse.status_code == 200:
                         user_ids.append(user_id)
            else:
                missing_fields = [field for field in expected_fields if field not in data]
                print(f"Missing fields: {', '.join(missing_fields)}")

    except Exception as e:
        print(f"webSocket Error: {str(e)}")

def recognize_face(message, websocket):
    try:
        user_id = id(websocket)  # Generate unique ID for each user
        if user_id not in user_face_encodings:
            # Load and store the user's face encoding
            user_picture = face_recognition.load_image_file(io.BytesIO(message))
            user_face_encodings[user_id] = face_recognition.face_encodings(user_picture)[0]
            return {"status": True, "message": "User registered", "data": user_id}

        unknown_picture = face_recognition.load_image_file(io.BytesIO(message))
        unknown_face_encodings = face_recognition.face_encodings(unknown_picture)

        if len(unknown_face_encodings) > 0:
            unknown_face_encoding = unknown_face_encodings[0]
        else:
            return {"status": True, "message": "No Face Detected", "data": 0}
        results = face_recognition.compare_faces([user_face_encodings[user_id]], unknown_face_encoding)

        print(results)
        if results[0] == True:
            return {"status": True, "message": "Recognition successful", "data": 2}
        else: 
            return {"status": False, "message": "Recognition unsuccessful", "data": 1}
    except Exception as e:
        return {"status": False, "message": str(e)}
    
if __name__ =='__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        websockets.serve(websocket_handler, "0.0.0.0", 8765)
    )
    loop.run_forever()
