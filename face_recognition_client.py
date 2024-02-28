import asyncio
import base64
import websockets
import json, io
from PIL import Image

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
         # Encode the compressed image bytes to a base64 string
        base64_image = base64.b64encode(compressed_image_bytes).decode('utf-8')
        # Create a JSON object with the image and any other data you want to send
        data_to_send = json.dumps({"image": base64_image,
                                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDkxMTAyMTEsInJvbGUiOiJST0xFX0dVRVNUIiwiaWF0IjoxNzA5MTEwMjAxfQ.NFMM6ooYjakDQXYRiWl8AwwDiZVrqe8DDnSRgsRrD-U",
                                    "fcmToken":"dKj1wRDRQ0AhtImYi4vhxF:APA91bEWmMrUH9BSPKz0frC6DwCkLtKJ0M93N8phMZfv92euMLT-7Za9HVtfgGWVqY5MNQ4CvaFSadnKJu5cts1tH28s_kIAwjbtE82Sxnv1R49rDZJm4KHE9KUiCJHyZ1cNLZD79mO1",
                                    "refreshToken":"eyJhbGciOiJIUzUxMiJ9.eyJyb2xlIjoiUk9MRV9VU0VSIiwianRpIjoiMzkiLCJpYXQiOjE3MDkxMTAxODYsImV4cCI6Mzc3MDkxMTAxODZ9.EaYHxoq4rJQ71ham4zhbk2B8yU0w-59phkvSInjmDW7bH08v9M0Kb4AFGEt_MVrqQlTDcXa-F8-0Jf8Pnzh-kA",
                                    "lang":"en"
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
