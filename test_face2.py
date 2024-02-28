import base64
import face_recognition
import asyncio
import websockets
import json, io
import requests
import numpy as np

baseUrl = 'http://10.17.24.1:8080'
user_sockets = {}

expected_fields = ["Authorization", "fcmToken", "refreshToken", "lang"]

user_face_encoding = np.array([-0.17074172, 0.07812507, 0.08236964, -0.02922146, -0.01920027, -0.08254959,
                               -0.09183867, -0.02900358, 0.11314897, -0.04685779, 0.2010667, 0.0091875,
                               -0.1760285, -0.04568482, -0.06863898, 0.07285462, -0.10650066, -0.06155955,
                               -0.0306052, -0.15783961, 0.12061378, 0.05142964, 0.04832843, 0.05339117,
                               -0.19803564, -0.29626986, -0.16064441, -0.10452675, 0.02814799, -0.08680592,
                               0.02255293, -0.06106091, -0.17999014, -0.01223225, 0.00469893, 0.12794159,
                               -0.07446897, -0.10738026, 0.17276722, 0.01302932, -0.02723244, -0.03283914,
                               -0.01303553, 0.27805388, 0.12169388, 0.02550888, 0.04535266, -0.0734043,
                               0.11630757, -0.20470861, 0.1742063, 0.14096303, 0.08912981, 0.12986147,
                               0.12931855, -0.09397436, 0.07316221, 0.16361168, -0.21665074, 0.06879236,
                               -0.02186138, 0.00356644, -0.0021606, -0.04487803, 0.18212903, 0.15183997,
                               -0.12088749, -0.12106384, 0.15812978, -0.15938742, 0.02230029, 0.09013858,
                               -0.06050645, -0.22132626, -0.24537562, 0.13319393, 0.41139156, 0.19402726,
                               -0.16338909, 0.02249693, -0.10695324, -0.07212457, 0.09566925, -0.00719607,
                               -0.12051937, 0.03433694, -0.11743093, 0.07077977, 0.18238118, -0.00269058,
                               -0.09401317, 0.23385736, 0.03304033, 0.05327794, 0.09742468, 0.03967848,
                               -0.12700677, 0.00889105, -0.06070563, 0.03692862, 0.04746502, -0.12206486,
                               -0.04533466, 0.02486343, -0.10114935, 0.14422543, 0.0476535, -0.05634858,
                               -0.08630971, 0.02662708, -0.27572367, -0.06957806, 0.15648983, -0.31048664,
                               0.18430705, 0.12823772, 0.0383493, 0.23552805, 0.10297075, 0.09977164,
                               0.00935903, -0.09216777, -0.05859243, -0.02676699, 0.05431541, 0.04054001,
                               0.04190234, 0.05283551])

async def websocket_handler(websocket, path):
    try:
        user_id = id(websocket)
        print("user_id")
        print(user_id)
        user_sockets[user_id] = websocket

        async for message in websocket:
            # Decode the received JSON message
            data = json.loads(message)
            if all(field in data for field in expected_fields):

                if user_id in user_sockets:
                    await start_recognize_face(websocket, data["image"], user_face_encoding)
                else:
                     # Call the function in your websocket_handler
                     api_response = await refresh_token(data, baseUrl)
                     if api_response.status_code == 200:
                         await start_recognize_face(websocket, data["image"], user_face_encoding)
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
