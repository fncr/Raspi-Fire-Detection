import json, requests, os, random, sys
from PIL import Image, ImageDraw

#make a prediction on the image
model_id = os.environ.get('NANONETS_MODEL_ID')
api_key = os.environ.get('NANONETS_API_KEY')
for n in range(10):
    image_path = str(sys.argv[1]) + "/image" + str(n) + ".jpg"

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
        if i["score"] > .95:
            draw.rectangle((i["xmin"],i["ymin"], i["xmax"],i["ymax"]), fill=(random.randint(1, 255),random.randint(1, 255),random.randint(1, 255),127))

    im.save("image2.jpg")
    os.system("xdg-open image2.jpg")
