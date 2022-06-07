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
#Meghatározzuk az alapkönyvtárat és azon belül az adathalmaz mappát
baseDirectory = os.path.dirname(os.path.abspath(__file__))
imgDirectory = os.path.join(baseDirectory, "dataset")
#Inicializáljuk az arduinot, későbbi használatra
arduino = pyfirmata.Arduino("COM3") #Arduino meghívása #ARDUINO SZÜKSÉGES A FUTTATASHOZ

#Meghatározzuk a CV2-es haarcascade segítségével, hogy milyen alakzatokat keresünk, jelen esetben fejeket.
face_data = cv2.CascadeClassifier("haarcascade/haarcascade_frontalface_alt2.xml")
#Létrehozzuk az arc felismerőt
recognizer = cv.face.LBPHFaceRecognizer_create()
#Beolvassuk a képzett adatot, tehát a fejekről eltárolt információkat a gép "emlékeit"
recognizer.read("trainner.yml")

#Létrehozzuk a címkék könyvtárat és kiolvassuk belőle az eltárolt neveket
labels = {}
with open("labels.pickle", "rb") as file:
    originalLabels = pickle.load(file)
    labels = {v:k for k, v in originalLabels.items()}
#Inicializáljuk a webkamerát későbbi olvasáshoz.
capture = cv.VideoCapture(0)
#Létrehozzuk a Tkinteres grafikus interfész ablakját
window = tk.Tk()

#Meghatározzuk az ablak méretét és háttérszínét
window.geometry("500x150")
window.configure(bg="black")

#Megadjuk az ablak elemeit és változoit KEZD
tk.Label(window,text="FElvenni kívánt Ember Neve: ", font="10", bg="white", fg="black").pack()
newEntry = tk.Entry(window)
newEntry.pack()
var2 = tkinter.IntVar()
checkbox = tk.Checkbutton(window, text="Rendelkezik jogosultsággal?", variable=var2)
checkbox.pack()
tk.Label(window,text="válassza ki az új arcról képeket tartalmazó mappát:  ", font="10", bg="white", fg="black").pack()
tk.Button(window, text = "Mappa: ", command=lambda: chooseNewFaceDirectory(), width = 10).pack()
tk.Label(window,text="Amint kész van zárja indítsa újra a szoftvert!", font="10", bg="black", fg="red").pack()
#Megadjuk az ablak elemeit és változoit VÉGE

#Létrehozzuk az új profilt beolvasó függvényt
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
# jelenleg arcot felismerünk tartalmazó logikai változó
confLevels = False



try:
    #Létrehozzuk a fő iterációt, mellyel a webkamera élő képén megyünk folyamatosan végig
    while True:
        #Frissítjük a tkinter ablakot
        window.update()
        #Inicializáljuk a webkamera képét és folyamatosan beolvassuk
        _, img = capture.read()
        #Létrehozzuk a grayscale képet amelyet majd olvas a program.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #A Haarcascade által megadott arcfelismerő leírás segítségével megadjuk mit tekintünk arcnak
        faces = face_data.detectMultiScale(gray, 1.1, 4)
        #Végig iterálunk az összes arcon az összes kordinátán
        for (x,y,w,h) in faces:
            #Az arcra felírunk egy négyzetet ahol felismerünk valakit
            cv2.rectangle(img, (x,y),(x+w, y+h), (255,100,50),5)
            face_gray = gray[y: y+h, x: x+w]
            #Visszakérjük az arc felismerőtől azt az értéket miszerint mennyire biztos abban, hogy felismeri az arcot
            id_, conf = recognizer.predict(face_gray)
            #Ha ez az érték nagyobb egyenlő mint 60 de kisebb egyenlő 85 százalékkal abban az esetben kiírjuk a felhasználó nevét
            if conf >= 60 and conf <= 85:
                print(labels[id_])
                fontStyle = cv.FONT_ITALIC
                nameOfPerson = labels[id_]
                cv2.putText(img, nameOfPerson, (x,y),fontStyle,1, (255,255,255),2,cv.LINE_AA)
                print(f'{nameOfPerson}-AUTHORIZED.txt')
                #felismerünk arcot változó igaz
                confLevels = True
            else:
                confLevels = False

            #Profil felismerése
            try:
                #Ha a jelenleg felismert személyhez társítottunk 'UNAUTHORIZED' azaz nincs felhatalmazása azonosítot abban az esetben a piros ledet kapcsolja fel, és írja ki a személy nevét és azt hogy 'UNAUTHORIZED
                if os.path.isfile(os.path.join(imgDirectory, f'{nameOfPerson}-UNAUTHORIZED.txt')) == True and confLevels == True:
                    cv2.putText(img, f"{nameOfPerson} UnAuthorized", (x,y),fontStyle,1, (0,0,255),2,cv.LINE_AA)
                    arduino.digital[13].write(False)
                    arduino.digital[11].write(False) #ARDUINO SZÜKSÉGES A FUTTATASHOZ
                    arduino.digital[7].write(True)
                #Ha a jelenleg felismert személyhez társítottunk 'AUTHORIZED' azaz van felhatalmazása azonosítot abban az esetben a zöld ledet kapcsolja fel, és írja ki a személy nevét és azt hogy 'AUTHORIZED
                elif os.path.isfile(os.path.join(imgDirectory, f'{nameOfPerson}-AUTHORIZED.txt')) and confLevels == True:
                    cv2.putText(img, f"{nameOfPerson} Authorized", (x,y),fontStyle,1, (0,255,0),2,cv.LINE_AA)
                    arduino.digital[13].write(True)
                    arduino.digital[11].write(False)  #ARDUINO SZÜKSÉGES A FUTTATASHOZ
                    arduino.digital[7].write(False)
                #felismert arc, de nem eltárolt profil
                elif confLevels == False:
                    arduino.digital[13].write(False)
                    arduino.digital[11].write(True)  # ARDUINO SZÜKSÉGES A FUTTATASHOZ
                    arduino.digital[7].write(False)





            #Hiba kezelés sárga led felkapcsolása
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

