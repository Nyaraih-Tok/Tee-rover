from flask import Flask, render_template, request, jsonify, Response
import RPi.GPIO as GPIO
from picamera import PiCamera
import io

app = Flask(__name__)

# GPIO pins for motor control
in1 = 22
in2 = 24
in3 = 16
in4 = 10
en = 18
en2 = 8

# Setup for  GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.setup(en2, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)

p = GPIO.PWM(en, 1000)
p1 = GPIO.PWM(en2, 1000)
p.start(100)
p1.start(100)


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24

def gen_frames():
    stream = io.BytesIO()
    for _ in camera.capture_continuous(stream, format="jpeg", use_video_port=True):
        stream.seek(0)
        frame = stream.read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        stream.seek(0)
        stream.truncate()

@app.route('/')
def index():
    return render_template('home.html')  

@app.route('/motor', methods=['POST'])
def motor_control():
    command = request.json.get('command')

    if command == 'forward':
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)
        return jsonify({'status': 'motors moving forward'})

    elif command == 'backward':
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in4, GPIO.HIGH)
        return jsonify({'status': 'moving in reverse now'})

    elif command == 'left':
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)
        return jsonify({'status': 'moving in left direction'})

    elif command == 'right':
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)
        return jsonify({'status': 'moving in the right direction'})

    elif command == 'high':
        p.ChangeDutyCycle(100)
        p1.ChangeDutyCycle(100)
        return jsonify({'status': 'motor speed set to high'})

    elif command == 'medium':
        p.ChangeDutyCycle(50)
        p1.ChangeDutyCycle(50)
        return jsonify({'status': 'motor speed set to medium'})

    elif command == 'low':
        p.ChangeDutyCycle(25)
        p1.ChangeDutyCycle(25)
        return jsonify({'status': 'motor speed set to low'})

    elif command == 'stop':
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)
        return jsonify({'status': 'motors stopped'})

    elif command == 'exit':
        GPIO.cleanup()
        return jsonify({'status': 'GPIO cleanup done'})

    else:
        return jsonify({'status': 'invalid command'}), 400

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
