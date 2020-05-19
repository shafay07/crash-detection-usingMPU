import time
import os
import numpy as np
import cv2

def recordVideo():
    cap = cv2.VideoCapture(0)
    print("*** Init Video Recording...***")
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('/home/pi/crash.mp4',fourcc, 20.0, (640,480))
    t0 = time.time()
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            print("Recording...")
            # write the flipped frame
            out.write(frame)
        else:
            break
        t1 = time.time()
        if t1-t0 >= 15:
            print('15 seconds recorded...Deleting old!')
            break;

    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Restarting recording...")
    recordVideo()
    
if __name__ == "__main__":
    recordVideo()
