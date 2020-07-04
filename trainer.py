import os
import cv2 
import numpy as np
from PIL import Image
import MySQLdb

recognizer = cv2.face.createLBPHFaceRecognizer()
path = 'dataSet'
db = MySQLdb.connect("localhost", "monitor", "password", "USER")
curs=db.cursor()
def getImagesWithID(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    faces = []
    IDs = []
    ID = 0
    USERNAME = ""
    for imagePath in imagePaths:
        faceImg=Image.open(imagePath).convert('L')
        faceNp=np.array(faceImg, 'uint8')
        #Chia de lay id cua tung anh rieng biet
        #ID = int(os.path.split(imagePath)[-1].split('.')[1])
        root = (os.path.split(imagePath)[-1].split('.')[1])
        ID = int(os.path.split(root)[-1].split('-')[0])
        USERNAME = (os.path.split(root)[-1].split('-')[1])
        faces.append(faceNp)
        IDs.append(ID)
        cv2.imshow("training", faceNp)
        cv2.waitKey(10)
    query = "INSERT INTO Info(ID, Username) values(%s, %s)"
    ## storing values in a variable
    values = (ID, USERNAME)
    ## executing the query with values
    curs.execute(query, values)

    #sql = """INSERT INTO Info(ID, Username) values(ID, USERNAME)"""
    #curs.execute(sql)
    db.commit()
    return IDs, faces

Ids,faces = getImagesWithID(path)
#training
recognizer.train(faces,np.array(Ids))
recognizer.save('recognizer/trainingData.yml')
cv2.destroyAllWindows()








