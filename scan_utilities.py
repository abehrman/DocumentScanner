import argparse
import os

import cv2
import pytesseract
from PIL import Image
from skimage.filters import threshold_local

import imutils
from transform import four_point_transform


def OCR(image, box):
    text_filename = "{}_text.png".format(os.getpid())
    cv2.imwrite(text_filename, imutils.crop(image, **box))
    cv2.imshow(text_filename, cv2.imread(text_filename))
    cv2.waitKey(1000)
    cv2.destroyWindow(text_filename)
    text = pytesseract.image_to_string(Image.open(text_filename)).split('\n')
    os.remove(text_filename)
    if isinstance(text, list):
        for line in text:
            try:
                line.encode('ascii')
                return line
            except:
                pass

        return "bad read"

    return text



    return text


def prepare_image(image, straighten, preprocess):
    image = cv2.imread(image)
    orig = image.copy()

    # convert the image to grayscale, blur it, and find edges
    # in the image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = cv2.GaussianBlur(image, (5, 5), 0)
    if straighten:
        ratio = image.shape[0] / 500.0
        image = imutils.resize(image, height=500)
        edged = cv2.Canny(image, 75, 200)

        # contours = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1:]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

        # loop over the contours
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # if our approximated contour has four points, then we
            # can assume that we have found our screen
            if len(approx) == 4:
                screenCnt = approx
                break

        # show the contour (outline) of the piece of paper
        # print
        # "STEP 2: Find contours of paper"
        # cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
        # cv2.imshow("Outline", image)
        # cv2.waitKey(5000)
        # cv2.destroyAllWindows()

        # apply the four point transform to obtain a top-down
        # view of the original image
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

        # convert the warped image to grayscale, then threshold it
        # to give it that 'black and white' paper effect
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        #warped = threshold_local(warped, 251, offset=10)
        warped = warped.astype("uint8") * 255

        image = warped

    if preprocess == "thresh":
        image = cv2.threshold(image, 0, 255,
                              cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    elif preprocess == "blur":
        image = cv2.medianBlur(image, 3)

    image = imutils.resize(image, height=500)

    filename = "{}_prepped.png".format(os.getpid())
    cv2.imwrite(filename, image)

    return filename


def process_image(image, boxes):
    ### load the image as a PIL/Pillow image, apply OCR, and then delete
    ### the temporary file
    # text = pytesseract.image_to_string(Image.open(filename))
    # os.remove(filename)
    # print(text)

    for box in boxes:
        box['value'] = OCR(image, {'start_x': int(box['start'][0]),
                                   'end_x': int(box['end'][0]),
                                   'start_y': int(box['start'][1]),
                                   'end_y': int(box['end'][1])})

        print('{}: {}'.format(box['name'],box['value']))

    return boxes


if __name__ == "__main__":
    # set path to OCR
    #    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ABehrman\Programming\Python\DocumentScanner\tess\tesseract.exe"

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
                    help="path to input image to be OCR'd")
    ap.add_argument("-p", "--preprocess", type=str, default="blur",
                    help="type of preprocessing to be done")
    ap.add_argument("-s", "--straighten", type=bool, default=True,
                    help="option to straighted image, True/False")
    args = vars(ap.parse_args())
    # load the image and compute the ratio of the old height
    # to the new height, clone it, and resize it

    prepare_image(args["image"], args['straighten'], args["preprocess"])
