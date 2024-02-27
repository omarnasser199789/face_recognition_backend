import face_recognition
import asyncio
import websockets
import json, io
import requests


url = 'https://myybs.ybservice.com:6443/v2/checkStatus'


# Dictionary to store user face encodings
user_face_encodings = {}
apiResponse = requests.get(url)
print(apiResponse.status_code)

async def websocket_handler(websocket, path):
    try:
        apiResponse = requests.get(url)
        print(apiResponse.status_code)
        if apiResponse.status_code == 200:
            async for message in websocket:
                response = recognize_face(message, websocket)
                await websocket.send(json.dumps(response))
    except Exception as e:
        print(f"webSocket Error: {str(e)}")

def recognize_face(message, websocket):
    try:
        print(1)
        user_id = id(websocket)  # Generate unique ID for each user
        if user_id not in user_face_encodings:
            # Load and store the user's face encoding
            user_picture = face_recognition.load_image_file(io.BytesIO(message))
            user_face_encodings[user_id] = face_recognition.face_encodings(user_picture)[0]
            return {"status": True, "message": "User registered", "data": user_id}

        unknown_picture = face_recognition.load_image_file(io.BytesIO(message))
        unknown_face_encodings = face_recognition.face_encodings(unknown_picture)
        print(2)
        if len(unknown_face_encodings) > 0:
            unknown_face_encoding = unknown_face_encodings[0]
        else:
            return {"status": True, "message": "No Face Detected", "data": 0}
        results = face_recognition.compare_faces([user_face_encodings[user_id]], unknown_face_encoding)
        print(4)
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
