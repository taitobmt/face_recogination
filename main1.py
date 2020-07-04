import RPi.GPIO as GPIO
from flask import Flask, render_template, Response, request, redirect, send_from_directory
from camera import VideoCamera
import threading 
import time
import os
import serial

GPIO.setwarnings(False)
button = 16
buttonSts = GPIO.LOW
ser = serial.Serial('/dev/ttyACM0',9600) 

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)


def gen(camera):
    while True:
        frame = camera.get_frame(True)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
def gen1(camera):
    while True:
        frame = camera.get_frame1()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    
@app.route('/')
def index():
    return render_template('index1.html')

#@app.route("/")
#def index():
#    # Read Sensors Status
#    buttonSts = GPIO.input(button)
#    templateData = {
#      'title' : 'GPIO input Status!',
#      'button'  : buttonSts,
#      }
#    while buttonSts:
#        print('aaas')
#    return render_template('index1.html')

@app.route('/add')
def cam():
    return render_template('add-face.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed1')
def video_feed1():
    return Response(gen1(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/add_face', methods = ['POST'])
def signup():
    id = request.form['id']
    username = request.form['username']
    print("The email address is '" + id + "'" + username)
    VideoCamera().add_face(id, username)
    return redirect('/trainner')

@app.route('/faceData/<filename>')
def send_image(filename):
    return send_from_directory("faceData", filename)

@app.route('/trainner', methods = ['GET'])
def get_gallery():
    image_names = sorted(os.listdir('./faceData'))[:10]
    return render_template("trainner.html", image_names=image_names)

@app.route('/list-unknow/<filename>')
def send_image1(filename):
    return send_from_directory("list-unknow", filename)

@app.route('/list-know/<filename>')
def send_image2(filename):
    return send_from_directory("list-know", filename)

@app.route('/list-unk', methods = ['GET'])
def get_unknow():
    string="undetect"+"\r"                          #Cong them ki tu \r
    ser.write(string.encode())
    image_names = (os.listdir('./list-unknow'))
    return render_template("list-unknow.html", image_names=image_names)

@app.route('/list-know', methods = ['GET'])
def get_know():
    string="undetect"+"\r"                          #Cong them ki tu \r
    ser.write(string.encode())
    image_names = (os.listdir('./list-know'))
    return render_template("list-know.html", image_names=image_names)

@app.route('/list-info', methods = ['GET'])
def get_info():
    string="undetect"+"\r"                          #Cong them ki tu \r
    ser.write(string.encode())
    persons = VideoCamera().list_info()
    return render_template("list-info.html", persons=persons);

@app.route('/confirm')
def confirm():
    VideoCamera().train()
    return redirect('/')

@app.route('/delete<id>')
def delete(id):
    idUser = id
    print('del' + idUser)
    VideoCamera().del_info(idUser)
    persons = VideoCamera().list_info()
    return render_template("list-info.html", persons=persons);


if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0')


