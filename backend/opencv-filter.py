import imutils
import cv2

MAX_VAL_THRESH = 100

def main():

    path = input("Enter path to video file: ")
    if containsMotion(path):
        print("File contains motion.")
    else:
        print("File does not contain motion.")


def convert(img):
    converted = imutils.resize(img, width=500)
    converted = cv2.cvtColor(converted, cv2.COLOR_BGR2GRAY)
    converted = cv2.GaussianBlur(converted, (21, 21), 0)
    return converted


def frameDiff(img1, img2):
    frameDelta = cv2.absdiff(img1, img2)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    dilated = cv2.dilate(thresh, None, iterations=2)
    nb = cv2.countNonZero(dilated)
    return nb

def containsMotion(filePath):

    videoCapture = cv2.VideoCapture(filePath)

    count = 0

    success, currentFrame = videoCapture.read()
    if not success:
        print('File read error in opencv-filter.containsMotion!')
        return False
    currentFrame = convert(currentFrame)

    # firstFrame = currentFrame
    prevFrame = currentFrame

    diffs = []

    while True:

        # firstDiff = frameDiff(currentFrame, firstFrame)
        prevDiff = frameDiff(currentFrame, prevFrame)

        diffs.append(prevDiff)

        prevFrame = currentFrame
        success, currentFrame = videoCapture.read()
        if not success:
            break
        currentFrame = convert(currentFrame)

        count += 1

    if max(diffs) > MAX_VAL_THRESH:
        return True
    else:
        return False

if __name__ == '__main__':
    main()
