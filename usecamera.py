from picamera import PiCamera
from time import sleep

camera = PiCamera()

def takePicture(i, x):
	filename = str(x) + '/image' + str(i) + '.jpg'
	camera.capture(filename)
	print("Image Saved to ", filename) 

camera.start_preview(alpha=200)
sleep(2)

for i in range (10):
	takePicture(i, "/home/pi/Projects/Python/NanoNets/FireDetection/FireImages")
	sleep(1)

camera.stop_preview()
