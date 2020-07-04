import cv2
face_cascade = cv2.CascadeClassifier("/home/pi/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_default.xml")
ds_factor=0.6

import RPi.GPIO as GPIO
import numpy as np
from PIL import Image
import os, shutil
import argparse
import MySQLdb
import time
import serial
import telepot
import threading
import shutil
import time
from datetime import datetime

#from telepot.loop import MessageLoop
class VideoCamera(object):
    ser = serial.Serial('/dev/ttyACM0',9600)  
    #Thiết lập động cơ Servo
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    #Thiết lập đè Led và nút bấm
    GPIO.setmode(GPIO.BOARD)
    # Đèn cho ta biết là camera đang quét mặt
    ledPin = 12
    # Chân nút nhấn để cho camera quét mặt
    buttonPin = 16


    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setwarnings(False)
    
    global path, db, curs

    path = 'dataSet'
    db = MySQLdb.connect("localhost", "monitor", "password", "USER")
    curs=db.cursor()
    
    
    def __init__(self):
        self.video = cv2.VideoCapture(0)
#        VideoCamera.get_frame1(self)
    def init(self):
        print("init")
        self.video = cv2.VideoCapture(0)

    def release(self):
        print("cleanup")
        GPIO.cleanup()
        self.video.release()
    
    def __del__(self):
        print("cleanup")
        GPIO.cleanup()
        self.video.release()
    
    def get_frame1(self):
        global path, db, curs
        string="detect"+"\r"                          #Cong them ki tu \r
        self.ser.write(string.encode())
        
        rec = cv2.face.createLBPHFaceRecognizer()
        #Load trained local binary pattern face data -- Tải dữ liệu  dữ liệu khuôn mặt dạng nhị phân đã được train
        rec.load("recognizer/trainingData.yml")
        font = cv2.FONT_HERSHEY_SIMPLEX
        success, image = self.video.read()
        image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        equ = cv2.equalizeHist(gray)
        rows,cols = equ.shape
        face_rects=face_cascade.detectMultiScale(gray,1.3,5)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if len(face_rects)==0:
            M = cv2.getRotationMatrix2D((cols/2,rows/2),-30,1)
       
        M = cv2.getRotationMatrix2D((cols/2,rows/2),30,1)
        dst = cv2.warpAffine(equ,M,(cols,rows))
        
        for (x,y,w,h) in face_rects:
             cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
             result = cv2.face.MinDistancePredictCollector()
             rec.predict(dst[y:y+h,x:x+w],result, 0)
             id = result.getLabel()
             conf = result.getDist()
             
             query = "SELECT Id FROM Info"
             curs.execute(query)
             ids = curs.fetchall()
             if((conf-50)<50):
                string="OpenDoor"+"\r"                          #Cong them ki tu \r
                self.ser.write(string.encode())
                sql_select_query = "select Username from Info where id = %s"
                curs.execute(sql_select_query, (id,))
                username = curs.fetchone()
                
                sql = "INSERT INTO detail(ID, Name, tdate, ttime) values(%s, %s, CURRENT_DATE(), NOW())"
                
                now = datetime.now()
                current_time = now.strftime("%y:%m:%d:%H:%M:%S")
                cv2.imwrite("list-know/"+str(id) + '-' + username[0] + '-' + current_time +".jpg", gray[y:y+h,x:x+w])
                value = (str(id), username[0])
                curs.execute(sql, value)

                db.commit()
             else: 
                id="Unknow_" + str(conf)
                now = datetime.now()
                current_time = now.strftime("%y:%m:%d:%H:%M:%S")
                sql = """INSERT INTO detail(ID, Name, tdate, ttime) values('00','Unknow', CURRENT_DATE(), NOW())"""
                curs.execute(sql)
                cv2.imwrite("list-unknow/Unknow" + '-' +current_time +".jpg", gray[y:y+h,x:x+w])
                #time.sleep(2)
                db.commit()
                
                string="UnKnown"+"\r"                       #Cong them ki tu \r
                self.ser.write(string.encode())
             cv2.putText(image,str(id),(x,y+h),font,1,(255,255,255),2,cv2.LINE_AA)  
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
        
    def list_info(self):
        global path, db, curs
        query = "SELECT * FROM Info"
        curs.execute(query)
        persons = curs.fetchall()
        return persons
        
     
    def get_frame(self, flat):
        global ret, img
        string="undetect"+"\r"                          #Cong them ki tu \r
        self.ser.write(string.encode())
        ret, img = self.video.read()
        if ret is True:
           gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        equ = cv2.equalizeHist(gray)
        faces = face_cascade.detectMultiScale(equ, 1.05, 5, minSize=(50,50))

        if(flat):
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                break
            ret, jpeg = cv2.imencode('.jpg', img)
            return jpeg.tobytes()
    
    def add_face(self, id, username):
        shutil.rmtree('faceData/')
        os.makedirs('faceData/') 
        
        sampleNum=0
        while(True):
            global ret, img 
            if ret is True:
               gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
               continue 
            equ = cv2.equalizeHist(gray)
            faces = face_cascade.detectMultiScale(equ, 1.05, 5, minSize=(50,50))
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                #incrementing sample number 
                sampleNum=sampleNum+1
                #saving the captured face in the dataset folder
                cv2.imwrite("faceData/User."+ id + '-' + username + '.' + str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
#                cv2.imwrite("faceData/User."+id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
#                cv2.imshow('frame',img)
                
                
            #wait for 1 miliseconds 
            if cv2.waitKey(150) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 20
            elif sampleNum>10:
                break
        self.video.release()
    
    def getImagesWithID(self):
        
        src_files = os.listdir('faceData')
        for file_name in src_files:
            full_file_name = os.path.join('faceData', file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, 'dataSet')
        
#        imgData = [os.path.join(path,f) for f in os.listdir('faceData')]
#        for i in imgData:
#            shutil.copy(i, 'dataSet')
        
        global path, db, curs
        recognizer = cv2.face.createLBPHFaceRecognizer()
        path = 'dataSet'
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
        faces = []
        IDs = []
        ID = 0
        USERNAME = ""
        for imagePath in imagePaths:
            faceImg=Image.open(imagePath).convert('L')
            faceNp=np.array(faceImg, 'uint8')
            
            root = (os.path.split(imagePath)[-1].split('.')[1])
            number = (os.path.split(imagePath)[-1].split('.')[2])
            ID = int(os.path.split(root)[-1].split('-')[0])
            USERNAME = (os.path.split(root)[-1].split('-')[1])
            if str(number) == '3':
               query = "INSERT IGNORE INTO  Info(ID, Username) values(%s, %s)"
               values = (ID, USERNAME)
               curs.execute(query, values)
               db.commit()
            faces.append(faceNp)
            IDs.append(ID)
            cv2.waitKey(10)
            
        return IDs, faces;

    def train(self):
        
        recognizer = cv2.face.createLBPHFaceRecognizer()
        Ids,faces = VideoCamera().getImagesWithID()
        #training
        recognizer.train(faces,np.array(Ids))
        recognizer.save('recognizer/trainingData.yml')
        
    def del_info(self, id):
        global db, curs

        sql_select_query = "delete from Info where id = %s"
        curs.execute(sql_select_query, (id,))
        path = 'dataSet'
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
        for imagePath in imagePaths:
            root = (os.path.split(imagePath)[-1].split('.')[1])
            ID = int(os.path.split(root)[-1].split('-')[0])
            print('ID' + str(ID) + '-' + id)
            if str(ID) == str(id):
                os.remove(imagePath)
    
        db.commit()
        VideoCamera().train()
        
