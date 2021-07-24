import cv2, json, requests, os, math
from twilio.rest import Client
from gps import *

#sending text stuff

# def makeLink(lon, lat):                         #broken
#     link = "https://www.google.com/maps/place/" + str(lat) + "" + str(lon)
#     return link


def convertCoords(lon_raw_coord, lat_raw_coord):
    lon_axis = "E"
    lat_axis = "N"

    if lon_raw_coord[0] == "-":
        lon_axis = "W"
        lon_raw_coord = lon_raw_coord[1::]

    if lat_raw_coord[0] == "-":
        lat_axis = "S"
        lat_raw_coord = lat_raw_coord[1::]

    lat = str(convertDMS(lat_raw_coord) + lat_axis)
    lon = str(convertDMS(lon_raw_coord) + lon_axis)
    return lat, lon


def convertDMS(x):
    print(x)
    x = float(x)
    degrees = math.trunc(x)
    m = (x - degrees) * 60
    minutes = math.trunc(m)
    seconds = round(((m - minutes) * 60), 1)

    dmsString = str(degrees) + "°" + str(minutes) + "'" + str(seconds) + '"'

    return dmsString


def makeMessage(lat, lon):
    message = "Hello! I've Detected a Fire At " + lat + " " + lon
    return message


def sendMessage(message):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']

    client = Client(account_sid, auth_token)

    client.api.account.messages.create(
        to="+14086690761",
        from_="+13109296257",
        body=message)


def getPositionData(gps):
    nx = gpsd.next()
    # For a list of all supported classes and fields refer to:
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    if nx['class'] == 'TPV':
        latitude = str(getattr(nx, 'lat', "Unknown"))
        longitude = str(getattr(nx, 'lon', "Unknown"))
        lat, lon = convertCoords(longitude, latitude)
        sendMessage(makeMessage(lat, lon))
        return 1

def doMessage():
  x = 0
  while x != 1:
    x = getPositionData(gpsd)

#Machine Learning Model stuff
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
    array = [False] * 10  # start off with empty list with 10 frames of no fires detected
    doText = 0
    while True:
        _, frame = cap.read()
        cv2.imwrite(n, frame)
        prediction = feed(model_id, api_key, n)
                                                                    #man these indents are hot garbage
        fireDetected = False                                        #anyways fireDetected will be false unless there is at least one fire prediction
        # draw boxes on the image
        for i in prediction:
            if i["score"] > 0:
                percentVal = 'fire: ' + str(i["score"]*100) + '%'                   #draw image
                cv2.rectangle(frame,(i["xmin"],i["ymin"]+3), (i["xmax"],i["ymax"]), (0, 255, 0), 3)
                cv2.putText(frame, percentVal, (i["xmin"], i["ymin"]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                fireDetected = True

        hasFire = checkArray(array)
        if fireDetected and hasFire == 0:
            doMessage()
        array = makeArray(fireDetected, array)                   #do cooldown

        #cv2.rotate(frame, cv2.cv2.ROTATE_180_CLOCKWISE)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

#cooldown stuff
def checkArray(array):
    for i in array:
        if i == True:
            return 1
    return 0

def makeArray(input, array):
    del array[0]            #delete oldest number and add newest number
    array.append(input)
    return array

def main():
    model_id = os.environ.get('NANONETS_MODEL_ID')
    api_key = os.environ.get('NANONETS_API_KEY')

    n = '/home/pi/wkspace/FireImages/Frame.jpg'

    useCV(model_id, api_key, n)

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
main()
