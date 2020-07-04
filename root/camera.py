import cv2
face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
ds_factor=0.6

import RPi.GPIO as GPIO
import numpy as np
from PIL import Image
import os
import argparse
import MySQLdb
import time
import serial
import telepot
#from telepot.loop import MessageLoop

class VideoCamera(object):
    ser = serial.Serial('/dev/ttyACM0',9600)  
    #Thiết lập động cơ Servo
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7,GPIO.OUT)
    #Disable warnings (optional)
    GPIO.setwarnings(False)
    #chân số 7 (GPIO4)
    servo=GPIO.PWM(7,50)
    #động cơ lúc bắt đầu sẽ ở vị trí khóa cửa


    #Thiết lập đè Led và nút bấm
    GPIO.setmode(GPIO.BOARD)

    # Đèn cho ta biết là camera đang quét mặt
    ledPin = 12


    # Chân nút nhấn để cho camera quét mặt
    buttonPin = 16


    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setwarnings(False)

    #Thiết lập lưu dữ liệu vào Cơ sở dữ liệu Mysql
    db = MySQLdb.connect("localhost", "monitor", "password", "USER")
    curs=db.cursor()

    #Load pretrained cascade face detection -- Load file cơ sở nhận diện khuôn mặt (OpenCV)
    face_cascade = cv2.CascadeClassifier("/home/pi/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_default.xml")


    #Load the recognizer -- Tải file nhận dạng
    rec = cv2.face.createLBPHFaceRecognizer()
    #Load trained local binary pattern face data -- Tải dữ liệu  dữ liệu khuôn mặt dạng nhị phân đã được train
    rec.load("recognizer/trainingData.yml")
    id=0
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
        
    #cam = cv2.VideoCapture(0)

    def get_image():
        return cv2.VideoCapture(0).read()[1]

    
    def get_frame(self):
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
        #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
       
        M = cv2.getRotationMatrix2D((cols/2,rows/2),30,1)
        dst = cv2.warpAffine(equ,M,(cols,rows))
        
        for (x,y,w,h) in face_rects:
             cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
             result = cv2.face.MinDistancePredictCollector()
             rec.predict(dst[y:y+h,x:x+w],result, 0)
             id = result.getLabel()
             conf = result.getDist()
             if((conf-50)<50):
                 print("as")
#                for i in ids:
#                    if(id == i[0]):
#                        string="OpenDoor"+"\r"                          #Cong them ki tu \r
#                        ser.write(string.encode())
#    #                    query = "SELECT Username FROM `Info` WHERE id=%s"
#    #                    value = (str(id))
#    #                    curs.execute(query, value)
#                        sql_select_query = """select Username from Info where id = %s"""
#                        curs.execute(sql_select_query, (id,))
#                        username = curs.fetchall()
#                        sql = "INSERT INTO detail(ID, Name, tdate, ttime) values(%s, %s, CURRENT_DATE(), NOW())"
#                        value = (str(id), username[0])
#                        curs.execute(sql, value)
#                        cv2.imwrite("DataAsset/User."+str(id) +'.' + ".jpg", gray[y:y+h,x:x+w])
#                        db.commit()
             else:
                id="Unknow_" + str(conf)
#                sql = """INSERT INTO detail(ID, Name, tdate, ttime) values('00','Unknow', CURRENT_DATE(), NOW())"""
#                curs.execute(sql)
#                cv2.imwrite("DataAsset/Unknow"+id+'.' + ".jpg", gray[y:y+h,x:x+w])
#                #time.sleep(2)
#                db.commit()
                
                string="UnKnown"+"\r"                          #Cong them ki tu \r
#                ser.write(string.encode())
             cv2.putText(image,str(id),(x,y+h),font,1,(255,255,255),2,cv2.LINE_AA)  
        ret, jpeg = cv2.imencode('.jpg', image)
        
        
        return jpeg.tobytes()

    def detectFace():
        frame = self.video.read()[1];
        img = frame;
        faces = face_cascade.detectMultiScale(equ, 1.3, 5)
        dst = cv2.warpAffine(equ,M,(cols,rows))
        M = cv2.getRotationMatrix2D((cols/2,rows/2),30,1)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            result = cv2.face.MinDistancePredictCollector()
            rec.predict(hog[y:y+h,x:x+w],result, 0)
            id = result.getLabel()
            
            conf = result.getDist()
            
            query = "SELECT Id FROM Info"
            curs.execute(query)
            ids = curs.fetchall()
            if(conf<50):
                for i in ids:
                    if(id == i[0]):
                        string="OpenDoor"+"\r"                          #Cong them ki tu \r
                        ser.write(string.encode())
    #                    query = "SELECT Username FROM `Info` WHERE id=%s"
    #                    value = (str(id))
    #                    curs.execute(query, value)
                        sql_select_query = """select Username from Info where id = %s"""
                        curs.execute(sql_select_query, (id,))
                        username = curs.fetchall()
                        sql = "INSERT INTO detail(ID, Name, tdate, ttime) values(%s, %s, CURRENT_DATE(), NOW())"
                        value = (str(id), username[0])
                        curs.execute(sql, value)
                        cv2.imwrite("DataAsset/User."+str(id) +'.' + ".jpg", gray[y:y+h,x:x+w])
                        db.commit()
                        
                        
            else:
                id="Unknow_" + str(conf)
                sql = """INSERT INTO detail(ID, Name, tdate, ttime) values('00','Unknow', CURRENT_DATE(), NOW())"""
                curs.execute(sql)
                cv2.imwrite("DataAsset/Unknow"+id+'.' + ".jpg", gray[y:y+h,x:x+w])
                #time.sleep(2)
                db.commit()
                
                string="UnKnown"+"\r"                          #Cong them ki tu \r
                ser.write(string.encode())
            
            cv2.putText(img,str(id),(x,y+h),font,1,(255,255,255),2,cv2.LINE_AA)  
          

#    def action(msg):
#        chat_id = msg['chat']['id']
#        command = msg['text']
#        print ('Received: %s' % command)
#        if 'Open' in command:
#            string="OpenDoor"+"\r"                          #Cong them ki tu \r
#            ser.write(string.encode())
#            message = "The door is opened"
#            message = message 
#            telegram_bot.sendMessage (chat_id, message)
#        if 'Close' in command:
#            string="UnKnown"+"\r"                          #Cong them ki tu \r
#            ser.write(string.encode())
#            message = "The door is closed"
#            message = message
#            telegram_bot.sendMessage (chat_id, message)
#    telegram_bot = telepot.Bot('1098651132:AAFI3wBkyWSxIkfFhjbGDBvnjKDGY8x12Q8')
#    print (telegram_bot.getMe())
#    MessageLoop(telegram_bot, action).run_as_thread()
#    print ('Up and Running....')
#    while(True):
#        #read each frame in the real-time video -- Đọc từng Khung hình trực tiếp.
#
#        buttonState = GPIO.input(buttonPin)
#            
#        frame = get_image();
#        img = frame;
#        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#        equ = cv2.equalizeHist(gray)
#        faces = face_cascade.detectMultiScale(equ, 1.3, 5)
#        if len(faces)==0:
#            rows,cols = equ.shape
#            M = cv2.getRotationMatrix2D((cols/2,rows/2),30,1)
#            dst = cv2.warpAffine(equ,M,(cols,rows))
#            faces = face_cascade.detectMultiScale(dst, 1.3, 5)
#            if len(faces)==0:
#                rows,cols = equ.shape
#                M = cv2.getRotationMatrix2D((cols/2,rows/2),-30,1)
#                dst = cv2.warpAffine(equ,M,(cols,rows))
#                faces = face_cascade.detectMultiScale(dst, 1.3, 5)
#                #Nút được nhấn mới bắt đầu nhận diện và đèn led sáng.
#                if buttonState == False:
#                    GPIO.output(ledPin, GPIO.HIGH)
#                    detectFace(faces,dst,img)
#                    string="detect"+"\r"                          #Cong them ki tu \r
#                    ser.write(string.encode())
#                else:
#                    GPIO.output(ledPin, GPIO.LOW)
#                    string="undetect"+"\r"                          #Cong them ki tu \r
#                    ser.write(string.encode())
#            else:
#                #Nút được nhấn mới bắt đầu nhận diện và đèn led sáng
#                if buttonState == False:
#                    GPIO.output(ledPin, GPIO.HIGH)
#                    detectFace(faces,dst,img)
#                    string="detect"+"\r"                          #Cong them ki tu \r
#                    ser.write(string.encode())
#                else:
#                    GPIO.output(ledPin, GPIO.LOW)
#                    GPIO.output(ledPin, GPIO.LOW)
#                    string="undetect"+"\r"
#                    ser.write(string.encode())
# 
        
#    print("cleanup")
#    GPIO.cleanup()
#    cam.release()
#    cv2.destroyAllWindows()
