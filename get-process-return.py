import json, requests, os, random, sys, subprocess
from PIL import Image, ImageDraw
from picamera import PiCamera
from time import sleep

def feed(model_id, api_key, n):
    # make a prediction on the image
    image_path = str(sys.argv[1]) + "/TestImage.jpg"

    url = 'https://app.nanonets.com/api/v2/ObjectDetection/Model/' + model_id + '/LabelFile/'

    data = {'file': open(image_path, 'rb'),    'modelId': ('', model_id)}

    response = requests.post(url, auth=requests.auth.HTTPBasicAuth(api_key, ''), files=data)

    print("Image ", n, ":\n", response.text)

    #draw boxes on the image
    response = json.loads(response.text)
    im = Image.open(image_path)

    draw = ImageDraw.Draw(im, mode="RGBA")
    prediction = response["result"][0]["prediction"]

    for i in prediction:
        if i["score"] > .75:
            draw.rectangle((i["xmin"],i["ymin"], i["xmax"],i["ymax"]), fill=(random.randint(1, 255),random.randint(1, 255),random.randint(1, 255),127))

    p = subprocess.Popen('/home/pi/Projects/Python/NanoNets/FireDetection/object-detection-sample-python/code/imviewer.py')
    im.save("image2.jpg")
    p.kill()

def takePicture(x, camera):
    filename = str(x) + '/TestImage.jpg'
    camera.capture(filename)
    print("Image Saved to ", filename)

def main():
    camera = PiCamera()

    
    model_id = os.environ.get('NANONETS_MODEL_ID')
    api_key = os.environ.get('NANONETS_API_KEY')

    camera.start_preview(alpha=200)
    sleep(2)
    for n in range(10):
        takePicture("/home/pi/Projects/Python/NanoNets/FireDetection/FireImages", camera)
        feed(model_id, api_key, n)

main()
