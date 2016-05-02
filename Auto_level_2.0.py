 #-------------------------Auto_level 2.0 --------------------------------------

#!/usr/bin/python
# -*- coding: utf-8 -*-
#modules a importer 
import platform
import os,sys # systeme
import serial # communication serie
import time   # temps
from time import sleep

date=time.strftime("%Y-%m-%d")
heure=time.strftime("%H-%M-%S")

systeme=platform.platform()   #detection nom système

EntreeNomfichier=""
while EntreeNomfichier=="":
    EntreeNomfichier=input("nom du fichier de stockage  : ")
    if EntreeNomfichier=="":
        print ("Vous n'avez pas rentrez de nom!")
    if systeme=="Windows-10-10.0.10586-SP0":  # si Windows
        ser = serial.Serial('COM5',115200, timeout=1)  # ouverture port serie  
        print("connecté au port COM5")
        Nomfichier ='C:\\Users\\eric\\Documents\\3d\\table XY\\Auto level\\' + EntreeNomfichier +'.txt'
        if os.path.isfile(Nomfichier)==True:
            Nomfichier ='C:\\Users\\eric\\Documents\\3d\\table XY\\Auto level\\' + EntreeNomfichier +"_"+heure+'.txt'#Ajout heure au nom du fichier                                                                                                              
            print("le fichier existe ")                                                                              #pour eviter l'ecrasement du fichier
            continue
    else:  # Si autre systeme pour moi Linux
        Nomfichier='/home/eric/Table XYZ/'+ EntreeNomfichier +'.txt'
        if os.path.isfile(Nomfichier)==True:
            Nomfichier='/home/eric/Table XYZ/'+ EntreeNomfichier +"_"+heure+'.txt'#Ajout heure au nom du fichier pour eviter l'ecrasement du fichier
            print("le fichier existe ")
            #continue
        try:
            ser = serial.Serial('/dev/ttyACM0',115200, timeout=1)  # ouverture port serie
            print("connecté au port /dev/ttyACM0")
        except:
            ser = serial.Serial('/dev/ttyACM1',115200, timeout=1)  # ouverture port serie  si ttyACM0 n'est pas ouvert
            print("connecté au port /dev/ttyACM1")
        


Fichier=open(Nomfichier,'a') # Ouverture fichier en mode "append" on sait jamais
#-------------------------------------------------------------------------------
def FinDeCourse():# Recherche fin de course
    gcode="G54\n"
    envoiGCode(gcode) # envoi vers Arduino
    sleep(1)
    gcode="G01 Z0 F1\n"
    envoiGCode(gcode) # envoi vers Arduino
#-------------------------------------------------------------------------------
def Sortie(sortie): # Module sortie vers Arduino 
            sortie=str(sortie)
            sortie_byte=sortie.encode('ascii')
            ser.write(sortie_byte) 
            # fin sortie    
#-------------------------------------------------------------------------------
def envoiGCode(gcodeIn):
    stopGCode=False # variable classe pour stopper GCode
    flagOK=False # variable classe pour témoin bonne réception OK
    gcodeLines=gcodeIn.splitlines()
    print (gcodeLines)
		# défile les lignes du gcode
    for line in gcodeLines: # défile les lignes
        if line.startswith(';'):
            continue
        else :
            Sortie(line+"\n")  # envoie la chaine sur le port serie
            print ("envoi ligne : " + line )# lecture des données reçues
            flagOK=False
            chaineIn=""
            char=""
            while flagOK==False : # on attend réception <ok>				
					# reception d'une ligne
                    while (ser.inWaiting()): # tant que au moins un caractère en réception
                        char=ser.read() # on lit le caractère
                        if char=='\n': # si saut de ligne, on sort du while
							          #print("saut ligne reçu") # debug
                            char=''
                            break # sort du while inWaiting
                        else: #tant que c'est pas le saut de ligne, on l'ajoute à la chaine
                            char = char.decode(encoding="ascii")
                            chaineIn=chaineIn+char
                            if ser.inWaiting()==0 : # si aucun nouveau char en réception, on attend un peu...  
                                time.sleep(0.01) # pause en secondes
                                if stopGCode==True :
                                    stopGCode=False # RAZ variable
                                    return # sortie de la fonction 				
					# fin ser inWaiting				
					# analyse chaine recue
                                if chaineIn!="" :
                                    print (chaineIn)
                                    Fichier.write(chaineIn)
                                    if ">>" in chaineIn :  # deux >> car parfois le troisieme > n'arrive jamais ?
                                        flagOK=True
                                        break
                                    else: 
                                        chaineIn="" #RAZ chaineIn																						
    time.sleep(0.001) # pause en secondes entre 2 envoi			
		# fin for 
# fin envoiGcode           
#------------------------- Programme Principal --------------------------------
gcode=''      # Initialisation Variables
px=0          # Positions départs  X
py=0          #                    Y
pxmax=-1      # Positions Arrivées  X 
pymax=-1      #                     Y
pasx=-1       # Pas x et y
pasy=-1       #
sens=2        # Variable pour determiner le sens de déplacement sur l'axe Y

while pxmax <0 or pxmax>300:  # entrée position arrivée axe X pxmax 
    pxmax=input("dimension en X (0-300): ")
    try:
        pxmax=int(pxmax)
    except ValueError:
        print("Vous n'avez pas saisi de nombre")
        pxmax=-1
        continue
    if pxmax<0:
        print("Ce nombre est négatif !")
    if pxmax>300:
        print("chiffre trop grand (max 300)")
    
while pymax <0 or pymax>400: # entrée position arrivée axe Y pymax 
    pymax=input("dimension en Y (0-400): ")
    try:
        pymax=int(pymax)
    except ValueError:
        print("Vous n'avez pas saisi de nombre")
        pymax=-1
        continue
    if pymax<0:
        print("Ce nombre est négatif !")
    if pymax>400:
        print("chiffre trop grand (max 400)")

while pasx <1 or pasx>pxmax:  # entrée incrément en X
    pasx=input("Pas en X : ")
    try:
        pasx=int(pasx)
    except ValueError:
        print("Vous n'avez pas saisi de nombre")
        pasx=-1
        continue
    if pasx<1:
        print("Ce nombre est trop petit (mini=1)!")
    if pasx>pxmax:
        print("chiffre trop grand dimension en X=",pxmax)
        
while pasy <1 or pasy>pymax: # entrée incrément en Y
    pasy=input("Pas en Y ")
    try:
        pasy=int(pasy)
    except ValueError:
        print("Vous n'avez pas saisi de nombre")
        pasy=-1
        continue
    if pasy<1:
        print("Ce nombre est trop petit (mini=1)!")
    if pasy>pymax:
        print("chiffre trop grand dimension en Y=",pymax)

debut=0   # position départ en Y
fin=pymax # position final en Y

gcode='G28 X F8'    #Recherche Origine axe X
envoiGCode(gcode)
gcode='G28 Y F8'    #Recherche Origine axe Y
envoiGCode(gcode)
gcode='G28 Z F8'    #Recherche Origine axe Z
envoiGCode(gcode)
gcode='G01 Z5 F8'   #Déplacement axe Z 5mm vers le haut au cas ou  
envoiGCode(gcode)
gcode='G92 Z'       #Zero axe Z
envoiGCode(gcode)

stopGCode=False     #variable classe pour stopper GCode
flagOK=False        #variable classe pour témoin bonne réception OK
while px<=pxmax:
  debutBoucle, finBoucle=debut,fin
  if sens%2==0:   # si = zero --> Y croissant
      while debutBoucle<=finBoucle:
        Spx=str(px)
        Spy=str(debutBoucle)
        gcode =   "G01 X" +Spx+" Y"+Spy+" F8"
        print ("gcode=",gcode)
        envoiGCode(gcode)
        sleep(1)
        FinDeCourse()
        sleep(1) 
        debutBoucle=debutBoucle+(pasy)       

  else:            # si sens%2 != de zero --> Y décroissant
      finBoucle=fin
      while finBoucle>=debut:
        Spx=str(px)
        Spy=str(finBoucle)
        gcode =   "G01 X" +Spx+" Y"+Spy+" F8"
        print ("gcode=",gcode)
        envoiGCode(gcode)
        sleep(1)
        FinDeCourse()
        sleep(1)
        finBoucle=finBoucle+(pasy*-1)
  sens=sens+1    
  px=px+pasx
#------- Block de fin ----------------------------------------------------------  
print("Mise à zero des moteurs")
gcode='G01 X0 F8'   #Retour à zero axe X
envoiGCode(gcode)
gcode='G01 Y0 F8'   #Retour à zero axe Y
envoiGCode(gcode)
gcode='G28 Z F8'    #Recherche Origine axe Z
envoiGCode(gcode)
gcode="M18"         #Arret moteurs
envoiGCode(gcode)
Fichier.close()     #fermeture fichier
print("Termine")
os.system("pause")
