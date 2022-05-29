import tkinter

import cv2
import cv2 as cv
import numpy
import pickle
import pyfirmata
import time
import tkinter as tk
from tkinter import filedialog
import shutil
import os
baseDirectory = os.path.dirname(os.path.abspath(__file__))
imgDirectory = os.path.join(baseDirectory, "dataset")

#arduino = pyfirmata.Arduino("COM3")
img = cv.imread("dataset/image.jpg")

face_data = cv2.CascadeClassifier("haarcascade/haarcascade_frontalface_alt2.xml")
recognizer = cv.face.LBPHFaceRecognizer_create()
recognizer.read("trainner.yml")

labels = {}
with open("labels.pickle", "rb") as file:
    originalLabels = pickle.load(file)
    labels = {v:k for k, v in originalLabels.items()}
capture = cv.VideoCapture(0)

window = tk.Tk()


window.geometry("500x150")
window.configure(bg="black")
#tk.Label(window,text="Élő Kamera Kép", font="times new roman", bg="black",fg="red").pack()

tk.Label(window,text="FElvenni kívánt Ember Neve: ", font="10", bg="white", fg="black").pack()
newEntry = tk.Entry(window)
newEntry.pack()

var2 = tkinter.IntVar()

tk.Label(window,text="válassza ki az új arcról képeket tartalmazó mappát:  ", font="10", bg="white", fg="black").pack()
tk.Button(window, text = "Mappa: ", command=lambda: chooseNewFaceDirectory(), width = 10).pack()
checkbox = tk.Checkbutton(window, text="Rendelkezik jogosultsággal?", variable=var2)
checkbox.pack()
tk.Label(window,text="Amint kész van zárja indítsa újra a szoftvert!", font="10", bg="black", fg="red").pack()



def chooseNewFaceDirectory():
    newName = newEntry.get()
    folder_selected = filedialog.askdirectory()
    shutil.copytree(folder_selected, os.path.join(imgDirectory, newName))
    return folder_selected

def giveAuthToken(folder):
    if var2.get() == 1:
        file = open(f'{folder}/AUTHORIZED.txt', w)
        file.close()
    elif var2.get() == 0:
        file = open(f'{folder}/UNAUTHORIZED.txt', w)
        file.close()


try:

    while True:
        window.update()
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
                #cv2.putText(img, "Authorized", (0,50),fontStyle,1, (255,255,255),2,cv.LINE_AA)
                #if(nameOfPerson == "adrian"):
                    #arduino.digital[13].write(True) #Zöld
                #elif(nameOfPerson == "stevejobs"):
                    #arduino.digital[7].write(True) #Piros
                #else:
                    #arduino.digital[11].write(True) #Sárga

            #else:
                #arduino.digital[13].write(False)
                #arduino.digital[7].write(False)
                #arduino.digital[11].write(False)
            #cv2.imwrite(f'dataset/levi/img{x}.png', face_gray)

        cv2.imshow("ArcFelismeres", img)
        cv2.waitKey(1)
except(tk.TclError):
    import facestrain #Újra traineli a felismerőt

