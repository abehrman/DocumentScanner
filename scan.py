from transform import four_point_transform
import imutils
from PIL import Image
import pytesseract
import os

from skimage.filters import threshold_adaptive
import numpy as np
import argparse
import cv2


def OCR(image, box):
    text_filename = "{}_text.png".format(os.getpid())
    cv2.imwrite(text_filename, imutils.crop(image, **box))
    text = pytesseract.image_to_string(Image.open(text_filename))
    os.remove(text_filename)
    return text

if __name__ == "__main__":

    #set path to OCR
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ABehrman\Programming\Python\DocumentScanner\tess\tesseract.exe"

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
    image = cv2.imread(args["image"])
    straighten = args['straighten']
    orig = image.copy()


    # convert the image to grayscale, blur it, and find edges
    # in the image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = cv2.GaussianBlur(image, (5, 5), 0)
    if straighten:
        ratio = image.shape[0] / 500.0
        image = imutils.resize(image, height=500)
        edged = cv2.Canny(image, 75, 200)

        #contours = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

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
        #print
        #"STEP 2: Find contours of paper"
        #cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
        #cv2.imshow("Outline", image)
        #cv2.waitKey(5000)
        #cv2.destroyAllWindows()

        # apply the four point transform to obtain a top-down
        # view of the original image
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

        # convert the warped image to grayscale, then threshold it
        # to give it that 'black and white' paper effect
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        warped = threshold_adaptive(warped, 251, offset=10)
        warped = warped.astype("uint8") * 255

        image = warped

    #straighten = False


    name = {'start_y': 109,
            'end_y': 820,
            'start_x': 405,
            'end_x': 470}



    # show the original and scanned images
    #cv2.imshow("Original", imutils.resize(orig, height=650))
    #cv2.imshow("Scanned", imutils.resize(warped, height=650))
    #cv2.waitKey(5000)
    #cv2.destroyAllWindows()

    if args["preprocess"] == "thresh":
        image = cv2.threshold(image, 0, 255,
                             cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    elif args["preprocess"] == "blur":
        image = cv2.medianBlur(image, 3)

    ##filename = "{}.png".format(os.getpid())
    ##cv2.imwrite(filename, image)



    ### load the image as a PIL/Pillow image, apply OCR, and then delete
    ### the temporary file
    #text = pytesseract.image_to_string(Image.open(filename))
    #os.remove(filename)
    #print(text)
    start_x = 109
    end_x = 820

    name = OCR(image,{'start_x': start_x,'end_x': end_x,'start_y': 415,'end_y': 480})
    title = OCR(image, {'start_x': start_x, 'end_x': end_x, 'start_y': 480, 'end_y': 545})
    role = OCR(image, {'start_x': start_x, 'end_x': end_x, 'start_y': 545, 'end_y': 610})

    start_x = 855
    end_x = 1700

    dept = OCR(image, {'start_x': start_x, 'end_x': end_x, 'start_y': 415, 'end_y': 480})
    street = OCR(image, {'start_x': start_x, 'end_x': end_x, 'start_y': 480, 'end_y': 545})
    cityStateZip = OCR(image, {'start_x': start_x, 'end_x': end_x, 'start_y': 545, 'end_y': 610})
    tel = OCR(image, {'start_x': start_x, 'end_x': end_x, 'start_y': 610, 'end_y': 675})
    cell = OCR(image, {'start_x': start_x, 'end_x': end_x, 'start_y': 675, 'end_y': 740})
    email = OCR(image, {'start_x': start_x, 'end_x': end_x, 'start_y': 740, 'end_y': 805})

    print("""
name:\t{0}
title:\t{1}
role:\t{2}

dept:\t{3}
street:\t{4}
city:\t{5}
tel:\t{6}
cell:\t{7}
email:\t{8}
""".format(
        name,
        title,
        role,
        dept,
        street,
        cityStateZip,
        tel,
        cell,
        email
    ))
    #Name extraction
    #box = {'start_y': 109,
    #        'end_y': 820,
    #        'start_x': 405,
    #        'end_x': 470}
    #text_filename = "{}_text.png".format(os.getpid())
    #cv2.imwrite(text_filename, imutils.crop(image, **box))
    #name = pytesseract.image_to_string(Image.open(text_filename))
    #os.remove(text_filename)
    #print(name)

    #title_box = {'start_x': 109,
    #            'end_x': 820,
    #            'start_y': 472,
    #            'end_y': 540}
    #name_text_filename = "{}_name.png".format(os.getpid())
    #cv2.imwrite(name_text_filename, imutils.crop(image, **title_box))
    #name = pytesseract.image_to_string(Image.open(name_text_filename))
    #os.remove(name_text_filename)
    #print(name)

    # show the output images
    #cv2.imshow("Image", image)
    #cv2.imshow("Output", warped)
    #cv2.waitKey(5000)
    #cv2.destroyAllWindows()