import cv2, json, requests, os
import time

def feed(model_id, api_key, n):
    # make a prediction on the image
    image_path = n

    url = 'https://app.nanonets.com/api/v2/ObjectDetection/Model/' + model_id + '/LabelFile/'

    data = {'file': open(image_path, 'rb'),    'modelId': ('', model_id)}

    response = requests.post(url, auth=requests.auth.HTTPBasicAuth(api_key, ''), files=data)
    response = json.loads(response.text)

    prediction = response["result"][0]["prediction"]

    return prediction


def useCV(model_id, api_key, n):
    cap = cv2.VideoCapture(0)
    while True:
        _, frame = cap.read()
        cv2.imwrite(n, frame)
        prediction = feed(model_id, api_key, n)

        # draw boxes on the image
        for i in prediction:
            if i["score"] > .75:
                percentVal = 'fire: ' + str(i["score"]*100) + '%'
                cv2.rectangle(frame,(i["xmin"],i["ymin"]+3), (i["xmax"],i["ymax"]), (0, 255, 0), 3)
                cv2.putText(frame, percentVal, (i["xmin"], i["ymin"]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
		cv2.rotate(frame, cv2.cv2.ROTATE_180_CLOCKWISE)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    model_id = os.environ.get('NANONETS_MODEL_ID')
    api_key = os.environ.get('NANONETS_API_KEY')

    n = '/home/pi/Projects/Python/NanoNets/FireDetection/FireImages/Frame.jpg'

    useCV(model_id, api_key, n)

	main()
