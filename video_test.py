#!/usr/bin/python3

import cv2  # Script Last Updated - Release 1.1.2

print("Press ESC to exit.")

cv2.namedWindow("preview")
capture = cv2.VideoCapture(0)

ret_val = False

if capture.isOpened():  # try to get the first frame
    ret_val, image = capture.read()

while ret_val:
    cv2.imshow("preview", image)
    ret_val, frame = capture.read()
    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break
cv2.destroyWindow("preview")
