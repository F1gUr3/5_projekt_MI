#A SZOFTVER PONTOSSÁGÁHOZ NÖVELNI SZÜKSÉGES AZ ADATMENNYISÉGET
#
#
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

arduino = pyfirmata.Arduino("COM3") #Arduino meghívása #ARDUINO SZÜKSÉGES A FUTTATASHOZ
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

tk.Label(window,text="FElvenni kívánt Ember Neve: ", font="10", bg="white", fg="black").pack()
newEntry = tk.Entry(window)
newEntry.pack()

var2 = tkinter.IntVar()


checkbox = tk.Checkbutton(window, text="Rendelkezik jogosultsággal?", variable=var2)
checkbox.pack()
tk.Label(window,text="válassza ki az új arcról képeket tartalmazó mappát:  ", font="10", bg="white", fg="black").pack()
tk.Button(window, text = "Mappa: ", command=lambda: chooseNewFaceDirectory(), width = 10).pack()
tk.Label(window,text="Amint kész van zárja indítsa újra a szoftvert!", font="10", bg="black", fg="red").pack()

def chooseNewFaceDirectory():
    newName = newEntry.get()
    newName = str(newName).lower()
    folder_selected = filedialog.askdirectory()
    shutil.copytree(folder_selected, os.path.join(imgDirectory, newName))
    if var2.get() == 1:
        file = open(f'dataset/{str(newName).lower()}-AUTHORIZED.txt', mode="w")
        file.close()
    elif var2.get() == 0:
        file = open(f'dataset/{str(newName).lower()}-UNAUTHORIZED.txt', mode="w")
        file.close()
    return folder_selected

confLevels = False



try:

    while True:
        #Kikapcsolja a hiba jelző ledet
        arduino.digital[11].write(False)

        window.update()
        _, img = capture.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_data.detectMultiScale(gray, 1.1, 4)

        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y),(x+w, y+h), (255,100,50),5)
            face_gray = gray[y: y+h, x: x+w]
            id_, conf = recognizer.predict(face_gray)
            if conf >= 60 and conf <= 85:
                print(labels[id_])
                fontStyle = cv.FONT_ITALIC
                nameOfPerson = labels[id_]
                cv2.putText(img, nameOfPerson, (x,y),fontStyle,1, (255,255,255),2,cv.LINE_AA)
                print(f'{nameOfPerson}-AUTHORIZED.txt')
                confLevels = True
            else:
                confLevels = False


            try:
                if os.path.isfile(os.path.join(imgDirectory, f'{nameOfPerson}-UNAUTHORIZED.txt')) == True and confLevels == True:
                    cv2.putText(img, f"{nameOfPerson} UnAuthorized", (x,y),fontStyle,1, (0,0,255),2,cv.LINE_AA)
                    arduino.digital[13].write(False)
                    arduino.digital[11].write(False) #ARDUINO SZÜKSÉGES A FUTTATASHOZ
                    arduino.digital[7].write(True)
                elif os.path.isfile(os.path.join(imgDirectory, f'{nameOfPerson}-AUTHORIZED.txt')) and confLevels == True:
                    cv2.putText(img, f"{nameOfPerson} Authorized", (x,y),fontStyle,1, (0,255,0),2,cv.LINE_AA)
                    arduino.digital[13].write(True)
                    arduino.digital[11].write(False)  #ARDUINO SZÜKSÉGES A FUTTATASHOZ
                    arduino.digital[7].write(False)
                elif confLevels == False:
                    arduino.digital[13].write(False)
                    arduino.digital[11].write(True)  # ARDUINO SZÜKSÉGES A FUTTATASHOZ
                    arduino.digital[7].write(False)






            except(NameError):
                fontStyle = cv.FONT_ITALIC
                cv2.putText(img, "Error", (x + 100, y), fontStyle, 1, (255, 255, 255), 2, cv.LINE_AA)
                arduino.digital[13].write(False)
                #Felkapcsolja a hiba jelző ledet
                arduino.digital[11].write(True)  #ARDUINO SZÜKSÉGES A FUTTATASHOZ
                arduino.digital[7].write(False)
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

