# import the necessary packages
import cv2

def resize(image, height=None, width=None):
    if height != None and width != None:
        print(height, width)
        raise AttributeError("Can't specify both height and width")

    if height:
        r = height / image.shape[0]
        dim = (int(image.shape[1] * r), height)

    elif width:
        r = width / image.shape[1]
        dim = (width, int(image.shape[0] * r))


    # perform the actual resizing of the image and show it
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized

def rotate(image):
    # grab the dimensions of the image and calculate the center
    # of the image
    (h, w) = image.shape[:2]
    center = (w / 2, h / 2)

    # rotate the image by 180 degrees
    M = cv2.getRotationMatrix2D(center, 180, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))

    return rotated

def crop(image, start_x, end_x, start_y, end_y):
    cropped = image[start_x:end_x, start_y:end_y]

    return cropped