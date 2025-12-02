from picamera2 import Picamera2
picam2 = Picamera2()
picam2.start_and_capture_file("rover_test.jpg")
print("Rover camera test photo saved!")
