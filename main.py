import cv2
import cv2 as cv
import numpy
import pickle
import pyfirmata
import time

arduino = pyfirmata.Arduino("COM3")
img = cv.imread("dataset/image.jpg")

face_data = cv2.CascadeClassifier("haarcascade/haarcascade_frontalface_alt2.xml")
recognizer = cv.face.LBPHFaceRecognizer_create()
recognizer.read("trainner.yml")

labels = {}
with open("labels.pickle", "rb") as file:
    originalLabels = pickle.load(file)
    labels = {v:k for k, v in originalLabels.items()}
capture = cv.VideoCapture(0)

while True:
    _, img = capture.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_data.detectMultiScale(gray, 1.1, 4)

    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y),(x+w, y+h), (255,100,50),5)
        face_gray = gray[y: y+h, x: x+w]
        id_, conf = recognizer.predict(face_gray)
        if conf >= 45 and conf <= 85:
            print(labels[id_])
            fontStyle = cv.FONT_ITALIC
            nameOfPerson = labels[id_]
            cv2.putText(img, nameOfPerson, (x,y),fontStyle,1, (255,255,255),2,cv.LINE_AA)
            cv2.putText(img, "Authorized", (0,50),fontStyle,1, (255,255,255),2,cv.LINE_AA)
            if(nameOfPerson == "adrian"):
                arduino.digital[13].write(True) #Zöld
            elif(nameOfPerson == "stevejobs"):
                arduino.digital[7].write(True) #Piros
            else:
                arduino.digital[11].write(True) #Sárga

        else:
            arduino.digital[13].write(False)
            arduino.digital[7].write(False)
            arduino.digital[11].write(False)
        cv2.imwrite("dataset/Adrian/img10.png", face_gray)

    cv2.imshow("VId", img)
    cv2.waitKey(1)
