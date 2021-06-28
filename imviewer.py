from skimage.viewer import ImageViewer
from skimage.io import imread

img = imread('image2.jpg') #path to IMG
view = ImageViewer(img)
view.show()
