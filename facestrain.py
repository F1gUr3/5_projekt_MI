import os
import numpy
from PIL import Image
import cv2 as cv
import pickle

baseDirectory = os.path.dirname(os.path.abspath(__file__))
print(baseDirectory)
imgDirectory = os.path.join(baseDirectory, "dataset")

face_cascade = cv.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')

recognizer = cv.face.LBPHFaceRecognizer_create()

x_trainData = []
y_labelData = []
CurrentId = 0

labelIds = {}

for root, dirs, files in os.walk(imgDirectory):
    for file in files:
        if str(file).endswith("jpg") or str(file).endswith("png"):
            path = os.path.join(root, file)
            label = os.path.basename(os.path.dirname(path)).replace(" ", "-").lower()
            if label in labelIds:
                pass
            else:
                labelIds[label] = CurrentId
                CurrentId += 1
            id_ = labelIds[label]

            pillowImg = Image.open(path).convert("L")
            imageArray = numpy.array(pillowImg, "uint8")
            faces = face_cascade.detectMultiScale(imageArray, 1.1, 4)

            for (x,y,w,h) in faces:
                regionOfInterest = imageArray[y: y+h, x:x+w]
                x_trainData.append(regionOfInterest)
                y_labelData.append(id_)
#print(y_labelData)
#print(x_trainData)

with open("labels.pickle", "wb") as file:
    pickle.dump(labelIds, file)

recognizer.train(x_trainData, numpy.array(y_labelData))
recognizer.save("trainner.yml")