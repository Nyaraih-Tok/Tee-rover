from flask import Flask, render_template, request, jsonify, Response
import RPi.GPIO as GPIO
from picamera2 import PiCamera2 
import io

app = Flask(__name__)

# Motor Controller 1 (left motors) pins
in1 = 22
in2 = 24
in3 = 16
in4 = 10
en = 18
en2 = 8

# Motor Controller 2 (right motors) pins
in5 = 17
in6 = 27
in7 = 11
in8 = 23
en3 = 13
en4 = 19

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in [in1, in2, in3, in4, en, en2, in5, in6, in7, in8, en3, en4]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# PWM for speed control
p = GPIO.PWM(en, 100)
p1 = GPIO.PWM(en2, 100)
p2 = GPIO.PWM(en3, 100)
p3 = GPIO.PWM(en4, 100)
p.start(100)
p1.start(100)
p2.start(100)
p3.start(100)

# Camera setup
camera = PiCamera2()
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
        # Motor Controller 1 forward
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)
        # Motor Controller 2 forward
        GPIO.output(in5, GPIO.HIGH)
        GPIO.output(in7, GPIO.HIGH)
        GPIO.output(in6, GPIO.LOW)
        GPIO.output(in8, GPIO.LOW)
        return jsonify({'status': 'motors moving forward'})

    elif command == 'backward':
        # Motor Controller 1 backward
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in4, GPIO.HIGH)
        # Motor Controller 2 backward
        GPIO.output(in5, GPIO.LOW)
        GPIO.output(in7, GPIO.LOW)
        GPIO.output(in6, GPIO.HIGH)
        GPIO.output(in8, GPIO.HIGH)
        return jsonify({'status': 'motors moving backward'})

    elif command == 'left':
        # Left side motors backward
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in4, GPIO.HIGH)
        # Right side motors forward
        GPIO.output(in5, GPIO.HIGH)
        GPIO.output(in7, GPIO.HIGH)
        GPIO.output(in6, GPIO.LOW)
        GPIO.output(in8, GPIO.LOW)
        return jsonify({'status': 'turning left'})

    elif command == 'right':
        # Left side motors forward
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)
        # Right side motors backward
        GPIO.output(in5, GPIO.LOW)
        GPIO.output(in7, GPIO.LOW)
        GPIO.output(in6, GPIO.HIGH)
        GPIO.output(in8, GPIO.HIGH)
        return jsonify({'status': 'turning right'})

    elif command == 'high':
        p.ChangeDutyCycle(100)
        p1.ChangeDutyCycle(100)
        p2.ChangeDutyCycle(100)
        p3.ChangeDutyCycle(100)
        return jsonify({'status': 'motor speed set to high'})

    elif command == 'medium':
        p.ChangeDutyCycle(50)
        p1.ChangeDutyCycle(50)
        p2.ChangeDutyCycle(50)
        p3.ChangeDutyCycle(50)
        return jsonify({'status': 'motor speed set to medium'})

    elif command == 'low':
        p.ChangeDutyCycle(25)
        p1.ChangeDutyCycle(25)
        p2.ChangeDutyCycle(25)
        p3.ChangeDutyCycle(25)
        return jsonify({'status': 'motor speed set to low'})

    elif command == 'stop':
        for pin in [in1, in2, in3, in4, in5, in6, in7, in8]:
            GPIO.output(pin, GPIO.LOW)
        return jsonify({'status': 'motors stopped'})

    elif command == 'exit':
        GPIO.cleanup()
        return jsonify({'status': 'GPIO cleanup done'})

    else:
        return jsonify({'status': 'invalid command'}), 400

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
