from flask import Flask, render_template
from flask_socketio import SocketIO
import RPi.GPIO as GPIO

app = Flask(__name__)
socketio = SocketIO(app)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Define the pins for Motor 1 (Left)
pwm_pin_1 = 36  # Pin for PWM control
dir_pin_1 = 38  # Pin for direction control

# Define the pins for Motor 2 (Right)
pwm_pin_2 = 11  # Pin for PWM control
dir_pin_2 = 13  # Pin for direction control

# Set up the GPIO pins for Motor 1
GPIO.setup(pwm_pin_1, GPIO.OUT)
GPIO.setup(dir_pin_1, GPIO.OUT)
pwm_1 = GPIO.PWM(pwm_pin_1, 1000)

# Set up the GPIO pins for Motor 2
GPIO.setup(pwm_pin_2, GPIO.OUT)
GPIO.setup(dir_pin_2, GPIO.OUT)
pwm_2 = GPIO.PWM(pwm_pin_2, 1000)

@app.route('/')
def index():
    return render_template('index.html')
@socketio.on('control_motor')
def handle_motor_control(data):
    direction = data.get('direction', -1)
    speed = data.get('speed', 500)

    # Your motor control logic here
    if direction == 1:
        pwm_1.start(50)
        pwm_2.start(50)
        
        if speed > 1900:
            pwm_1.ChangeFrequency(1900)
            pwm_2.ChangeFrequency(1900)
        else:
            pwm_1.ChangeFrequency(speed)
            pwm_2.ChangeFrequency(speed)
            
        # Set the direction for both motors for pitch forward
        GPIO.output(dir_pin_1, GPIO.HIGH)
        GPIO.output(dir_pin_2, GPIO.HIGH)

    elif direction == 0:
        pwm_1.start(50)
        pwm_2.start(50)
        
        if speed > 1900:
            pwm_1.ChangeFrequency(1900)
            pwm_2.ChangeFrequency(1900)
        else:
            pwm_1.ChangeFrequency(speed)
            pwm_2.ChangeFrequency(speed)
            
        # Set the direction for both motors for pitch backward
        GPIO.output(dir_pin_1, GPIO.LOW)
        GPIO.output(dir_pin_2, GPIO.LOW)

    elif direction == 2:
        # Skid steering: Stop the right motor, left motor continues
        pwm_1.start(50)
        pwm_2.stop()

        if speed > 1900:
            pwm_1.ChangeFrequency(1900)
        else:
            pwm_1.ChangeFrequency(speed)

        # Set the direction for left motor
        GPIO.output(dir_pin_1, GPIO.HIGH)

    elif direction == 3:
        # Skid steering: Stop the left motor, right motor continues
        pwm_1.stop()
        pwm_2.start(50)

        if speed > 1900:
            pwm_2.ChangeFrequency(1900)
        else:
            pwm_2.ChangeFrequency(speed)

        # Set the direction for right motor
        GPIO.output(dir_pin_2, GPIO.HIGH)

    elif direction == 4:
        # Skid steering: Reduce the speed of the right motor, left motor remains the same
        pwm_1.start(50)
        pwm_2.start(50)

        if speed > 1900:
            pwm_1.ChangeFrequency(1900)
            pwm_2.ChangeFrequency(1500)  # Adjust the frequency for slower speed
        else:
            pwm_1.ChangeFrequency(speed)
            pwm_2.ChangeFrequency(speed - 400)

        # Set the direction for both motors
        GPIO.output(dir_pin_1, GPIO.HIGH)
        GPIO.output(dir_pin_2, GPIO.HIGH)

    elif direction == 5:
        # Skid steering: Reduce the speed of the left motor, right motor remains the same
        pwm_1.start(50)
        pwm_2.start(50)

        if speed > 1900:
            pwm_1.ChangeFrequency(1500)  # Adjust the frequency for slower speed
            pwm_2.ChangeFrequency(1900)
        else:
            pwm_1.ChangeFrequency(speed - 400)
            pwm_2.ChangeFrequency(speed)

        # Set the direction for both motors
        GPIO.output(dir_pin_1, GPIO.HIGH)
        GPIO.output(dir_pin_2, GPIO.HIGH)

    else:
        pwm_1.stop()
        pwm_2.stop()

    # Send feedback to the client
    socketio.emit('motor_status', {'success': True})

@socketio.on('connect')
def connect():
    print('Client connected')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=90)
    finally:
        pwm_1.stop()
        pwm_2.stop()
        GPIO.cleanup()
