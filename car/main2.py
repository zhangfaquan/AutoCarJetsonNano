import sys
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_motor import motor
from controller import PS4Controller
import camera
import datetime
import cv2
import csv

#init controller
ps4 = PS4Controller()
ps4.init()

#init i2c
i2c = busio.I2C(SCL, SDA)

#init PCA
pca = PCA9685(i2c)
pca.frequency = 50

servo_steer = servo.Servo(pca.channels[0])
esc = servo.ContinuousServo(pca.channels[1])

def scale_servo(x):
    y = round((30-70)*x+1/1+1+70,2) #used to scale -1,1 to 0,180
    return y

def scale_esc(x):
    y = round((x+1)/8,2) #used to scale -1,1 to 0,180
    return y
    
def drive(axis_data):
    servo_steer.angle = scale_servo(-axis_data[0])
    sum_inputs = round(-scale_esc(axis_data[4]) + scale_esc(axis_data[3]),2)
    esc.throttle = sum_inputs
    #print(sum_inputs)

def toggle(x):
    return not x

#init vars
train = False
trig = True
temp = 0

#init Camera
cam = camera.Camera()

#initial content
with open('control_data.csv','w') as f:
    f.write('date,steering,speed\n1,1,1\n') # TRAILING NEWLINE

def save_data(img,count,axis_data):

    if count!= temp:
        x = datetime.datetime.now()
        cv2.imwrite('images/'+str(x)+".jpg", img)
        
        with open('control_data.csv','a',newline='') as f:
            writer=csv.writer(f)
            writer.writerow([x,axis_data[0],axis_data[4]])
        temp = count
        print('Save data!')
    else:
        pass
        
        
print('Running!')

try:
    while True:
    
        button_data, axis_data, hat_data = ps4.listen()
        
        if button_data[1] == True and trig:
            train = toggle(train)
            trig = False
            
        elif button_data[1] == False:
            trig = True
        else:
            pass
        
        if train:
            drive(axis_data)
            if axis_data[4] >= 0.12:
                save_data(cam.value,cam.count,axis_data)
            else:
                print('Not saving img')
        else:
            pass            


except KeyboardInterrupt:
        pca.deinit()
        sys.exit(0)
        
