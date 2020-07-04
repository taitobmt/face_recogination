import cv2
detector=cv2.CascadeClassifier("/home/pi/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_default.xml")
cam = cv2.VideoCapture(0)
#id=input('vui long nhap id cua ban: ')
#username = input('Vui long nhap ten cua ban: ')
while True:
  id=input('vui long nhap id cua ban (khac "00"): ')
  if(id != '00'):
    break
while True:
  username = input('Vui long nhap ten cua ban (khac rong): ')
  if(username != ''):
    break
sampleNum=0
while(True):
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equ = cv2.equalizeHist(gray)
    faces = detector.detectMultiScale(equ, 1.05, 5, minSize=(50,50))
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        #incrementing sample number 
        sampleNum=sampleNum+1
        #saving the captured face in the dataset folder
        cv2.imwrite("dataSet/User."+ id + '-' + username + '.' + str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
        #cv2.imwrite("dataSet/User."+id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
        cv2.imshow('frame',img)
        
        
    #wait for 1 miliseconds 
    if cv2.waitKey(150) & 0xFF == ord('q'):
        break
    # break if the sample number is morethan 20
    elif sampleNum>10:
        break
cam.release()
cv2.destroyAllWindows()

