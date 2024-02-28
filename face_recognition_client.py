import asyncio
import base64
import websockets
import json, io
from PIL import Image
import numpy as np

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

def compress_image(image_path, quality=30):
    image = Image.open(image_path)
    compressed_image_stream = io.BytesIO()
    image.save(compressed_image_stream, format="JPEG", quality=quality)
    compressed_image_bytes = compressed_image_stream.getvalue()
    return compressed_image_bytes

async def recognize_face():
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as websoket:
        compressed_image_bytes = compress_image("me-2.JPG")
        #  Encode the compressed image bytes to a base64 string
        base64_image = base64.b64encode(compressed_image_bytes).decode('utf-8')
        # Create a JSON object with the image and any other data you want to send
        data_to_send = json.dumps({"image": base64_image,
                                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDkxMTAyMTEsInJvbGUiOiJST0xFX0dVRVNUIiwiaWF0IjoxNzA5MTEwMjAxfQ.NFMM6ooYjakDQXYRiWl8AwwDiZVrqe8DDnSRgsRrD-U",
                                    "fcmToken":"dKj1wRDRQ0AhtImYi4vhxF:APA91bEWmMrUH9BSPKz0frC6DwCkLtKJ0M93N8phMZfv92euMLT-7Za9HVtfgGWVqY5MNQ4CvaFSadnKJu5cts1tH28s_kIAwjbtE82Sxnv1R49rDZJm4KHE9KUiCJHyZ1cNLZD79mO1",
                                    "refreshToken":"eyJhbGciOiJIUzUxMiJ9.eyJyb2xlIjoiUk9MRV9VU0VSIiwianRpIjoiMzkiLCJpYXQiOjE3MDkxMTAxODYsImV4cCI6Mzc3MDkxMTAxODZ9.EaYHxoq4rJQ71ham4zhbk2B8yU0w-59phkvSInjmDW7bH08v9M0Kb4AFGEt_MVrqQlTDcXa-F8-0Jf8Pnzh-kA",
                                    "lang":"en",
                                    "userFaceEncoding": user_face_encoding.tolist() 
                                    })
        # Send the JSON string through the WebSocket channel
        await websoket.send(data_to_send)
        response = await websoket.recv()
        return json.loads(response)
    
async def main():
    try:
        response = await recognize_face()
        print(response)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
