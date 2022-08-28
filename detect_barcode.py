import imutils
import cv2

# reference: https://pyimagesearch.com/2014/11/24/detecting-barcodes-images-python-opencv/

image = cv2.imread('barcode database/img (1).jpg')
scale_percent = 20  # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)
image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

depth = cv2.CV_32F if imutils.is_cv2() else cv2.CV_32F
gradX = cv2.Sobel(gray, ddepth=depth, dx=1, dy=0, ksize=-1)
gradY = cv2.Sobel(gray, ddepth=depth, dx=0, dy=1, ksize=-1)

gradient = cv2.subtract(gradX, gradY)
gradient = cv2.convertScaleAbs(gradient)

blurred = cv2.blur(gradient, (5, 5))
_, thresh = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

closed = cv2.erode(closed, None, iterations=20)
closed = cv2.dilate(closed, None, iterations=30)

cv2.imshow("closed", closed)

cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

indent = 30  # (px)
width, height, _ = image.shape

for cnt in cnts:

    x, y, w, h = cv2.boundingRect(cnt)

    x1 = x - indent
    if x1 < 0:
        x1 = 0

    y1 = y - indent
    if y1 < 0:
        y1 = 0

    x2 = x + w + indent
    y2 = y + h + indent

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

cv2.imshow("Image", image)
cv2.waitKey(0)
