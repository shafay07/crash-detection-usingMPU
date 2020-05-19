import datetime
import os
import subprocess as sp
import smtplib 

from mpu6050 import mpu6050
from time import sleep 
import math
import matplotlib.pyplot as plt
sensor = mpu6050(0x68)

# pre-defined ranges
ACCEL_RANGE_2G = 0x00
ACCEL_RANGE_4G = 0x08
ACCEL_RANGE_8G = 0x10
ACCEL_RANGE_16G = 0x18

# crash-threshold
CRASH_THRESHOLD_2G = -2
CRASH_THRESHOLD_4G = -4
CRASH_THRESHOLD_8G = -8
CRASH_THRESHOLD_16G = -16

# set acceleration range
sensor.set_accel_range(accel_range = ACCEL_RANGE_8G)

# resultList for plot
resultList = []

def plotResult(result_list):
  lenList = range(len(result_list))
  x = [i[0] for i in result_list] 
  y = [i[1] for i in result_list] 
  z = [i[2] for i in result_list] 
  plt.plot(lenList,x)
  plt.plot(lenList,y)
  plt.plot(lenList,z)
  plt.legend(["accelX", "accelY", "accelZ"])
  plt.xlabel('Time period')
  plt.ylabel('Acceleration')
  plt.show()


def detectRollOver(acceleration_data):
  accelx = acceleration_data['x']
  accely = acceleration_data['y']
  accelz = acceleration_data['z']
  
  
  pitch = 180 * math.atan(accelx/math.sqrt(accely*accely + accelz*accelz))/math.pi
  roll = 180 * math.atan(accely/math.sqrt(accelx*accelx + accelz*accelz))/math.pi
  yaw = 180 * math.atan(accelz/math.sqrt(accelx*accelx + accelz*accelz))/math.pi
  if ((pitch < -30 or pitch > 30) or (roll > 30 or roll < -30)):
    print('Roll over detected with value...')
    print('{}, {}, {}'.format(pitch,roll,yaw))
    return True
  return False

def detectCrash(acceleration_data):
  if acceleration_data['x'] == CRASH_THRESHOLD_8G or acceleration_data['x'] == abs(CRASH_THRESHOLD_8G):
    print('A crash in X direction')
    return True
  elif  acceleration_data['y'] == CRASH_THRESHOLD_8G or acceleration_data['y'] == abs(CRASH_THRESHOLD_8G):
    print('A crash in y direction')
    return True
  elif acceleration_data['z'] == CRASH_THRESHOLD_8G or acceleration_data['z'] == abs(CRASH_THRESHOLD_8G):
    print('A crash in z direction')
    return True
  else:
    return False
  

def sendMail(rollOverStatus):
  # creates SMTP session 
  email = smtplib.SMTP('smtp.gmail.com', 587) 

  # TLS for security 
  email.starttls() 

  # authentication
  # compiler gives an error for wrong credential. 
  email.login("") 

  # message to be sent 
  SUBJECT = "Car accident detected"
  TEXT = "This is an automated car acciedent report. There is a car accident at *location* on: "+ str(datetime.datetime.now()) + " Roll over status is : " + str(rollOverStatus) + ". Please respond to this immediatly, Thanks" 
  message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

  # sending the mail 
  email.sendmail("", "", message) 

  # terminating the session 
  email.quit()

# main() of the script
if __name__ == "__main__":
  recordingProcess = sp.Popen(['python','/home/pi/record.py']) # runs recording.py 
  processStatus = sp.Popen.poll(recordingProcess) # status should be 'None'
  print(processStatus)
  print('Starting recording...')
  sleep(5)
  crashStatus = False
  
  while(True):
    # gets the data of acceleration in g
    accelerometer_data = sensor.get_accel_data(g = True)
    print(accelerometer_data)
    crashStatus = detectCrash(accelerometer_data)
 
    if crashStatus:
      print('A acciendent has detected...')
      print('Stopping the video...')
      sp.Popen.terminate(recordingProcess) # closes the process
      print('Done')
      print('Checking for roll over...')
      rollStatus = detectRollOver(accelerometer_data)
      print('Done')
      resultList.append(list(accelerometer_data.values()))
      print('Sending Email...')
      #sendMail(rollStatus)
      break;
    else:
      print('No crash...')
      resultList.append(list(accelerometer_data.values()))
  print('Plotting results...')
  plotResult(resultList)
  print('Done')
