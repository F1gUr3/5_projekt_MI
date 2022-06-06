# arduino.digital[7].write(True) #Piros
# arduino.digital[11].write(True) #Sárga
# arduino.digital[13].write(True) #Zöld
#arduino.digital[7].write(False)
#arduino.digital[11].write(False)
#arduino.digital[13].write(False)

import pyfirmata
import time

#[Teszt Szoftver]
# Ez a szoftver kizárólag az Arduino alaplap tesztelésére szolgál, amennyiben ez a szoftver hibát talál, hiba van a hardveres rétegben.

arduino = pyfirmata.Arduino("COM3")

while True:
    userInput = input("Melyik színt kapcsoljuk fel: (1-3)")
    if(userInput == "1"):
        arduino.digital[7].write(True) #Piros
    elif(userInput == "2"):
        arduino.digital[11].write(True) #Sárga
    elif(userInput == "3"):
        arduino.digital[13].write(True) #Zöld
    elif(userInput == "4"):
        arduino.digital[7].write(False)
        arduino.digital[11].write(False)
        arduino.digital[13].write(False)

