import base64
import face_recognition
import asyncio
import websockets
import json, io
import requests
import numpy as np

baseUrl = 'http://10.17.24.1:8080'
user_sockets = {}

expected_fields = ["Authorization", "fcmToken", "refreshToken", "lang", "userFaceEncoding"]

# picture_of_me = face_recognition.load_image_file("test-face.jpg")
# picture_of_me = face_recognition.load_image_file("me.png")
# my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]

async def websocket_handler(websocket, path):
    try:
        user_id = id(websocket)
        print("user_id")
        print(user_id)

        async for message in websocket:
            # Decode the received JSON message
            data = json.loads(message)
            if all(field in data for field in expected_fields):

                if user_id in user_sockets:
                    await start_recognize_face(websocket, data["image"], data["userFaceEncoding"])
                else:
                     # Call the function in your websocket_handler
                     api_response = await refresh_token(data, baseUrl)
                     if api_response.status_code == 200:
                         user_sockets[user_id] = websocket
                         await start_recognize_face(websocket, data["image"], data["userFaceEncoding"])
            else:
                missing_fields = [field for field in expected_fields if field not in data]
                print(f"Missing fields: {', '.join(missing_fields)}")

    except Exception as e:
        print(f"webSocket Error: {str(e)}")
    finally:
        del user_sockets[user_id]

async def refresh_token(data, baseUrl):
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
    apiResponse = requests.post(f'{baseUrl}/refreshToken', json=bodyData, headers=headers)
    print(apiResponse.status_code)

    return apiResponse

async def start_recognize_face(websocket, base64_image, user_face_encoding):
    try:
        # Decode the base64-encoded image data
        image_bytes = base64.b64decode(base64_image)
        # Process the image using face_recognition
        response = recognize_face(image_bytes, user_face_encoding)
        await websocket.send(json.dumps(response))
    except Exception as e:
        print(f"Error in start_recognize_face: {str(e)}")

def recognize_face(message, user_face_encoding):
    try:
        unknown_picture = face_recognition.load_image_file(io.BytesIO(message))
        unknown_face_encodings = face_recognition.face_encodings(unknown_picture)

        if len(unknown_face_encodings) > 0:
            unknown_face_encoding = unknown_face_encodings[0]
        else:
            return {"status": True, "message": "No Face Detected", "data": 0}
        
        results = face_recognition.compare_faces([user_face_encoding], unknown_face_encoding)

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
