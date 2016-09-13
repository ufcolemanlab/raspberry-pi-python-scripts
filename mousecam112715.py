## Script for Raspberry Pi and Pi camera (picameraUnoTrigger_2.py as mousecam.py)
##    - Camera on / off controlled by trigger input (HI/LO)
##    - Default is rot = 180, 640 x 480, 90 fps... parameters can be modified in picamVideo and picamPreview functions
##    - Default uses GPIO24 as pull_up with Arduino pin and GPIO17 controls indicator LED
## v1.0 7/28/14 by Jason Coleman
## v1.5 4/8/15 by Jason Coleman
## v2.0 7/14/15 by Jason Coleman - fixed trigger for Arduino

import RPi.GPIO as GPIO
import time, os, picamera, subprocess, sys
from time import gmtime, strftime

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # GPIO24 for trigger input
GPIO.setup(17, GPIO.OUT) # GPIO17 for LED

vidfps = 25 #fps

# Generate unique file directory
# target_dir = "/media/PICAM/" #/"/home/pi/picam_vids/" #"/media/Rikki1_NTFS/MouseData/" #USBs
# unique_dir = strftime("%Y%m%d_%H%M%S")
global data_dir
global unique_dir
data_dir = "/home/pi/MousecamData/"
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)
unique_dir = raw_input("Enter unique directory name for saving data (e.g.: NxHx_112715_day1): ")
target_dir = data_dir+"mousecam_"+unique_dir+"/"
# create new directory if directory does not exist
if not os.path.isdir(target_dir):
    os.makedirs(target_dir)   
    print("*** Files will be saved to "+target_dir+" for this session ***")

# Functions
def picamPreview(preview_secs):
    with picamera.PiCamera() as camera:
        print("Starting preview...please wait...")
        camera.rotation = 0
        camera.start_preview()
        time.sleep(preview_secs)
        #camera.capture(img_filename)
        camera.stop_preview()
        
def picamVideo(starttime,vidfps):
    with picamera.PiCamera() as camera:
        camera.resolution = (640,480)
        camera.framerate = vidfps
        camera.rotation = 0       #starttime = strftime("%Y-%m-%d %H:%M:%S")
        print("Started recording at "+starttime)
        camera.start_recording(target_dir+vid_filename)
        GPIO.wait_for_edge(24, GPIO.FALLING) # May need to change to GPIO.rising depending on input trigger (vs .FALLING)
        stoptime = strftime("%Y-%m-%d %H:%M:%S")
        print("Stopped recording at "+stoptime)
        camera.stop_recording()

def queryPreview():
    while True:
        GPIO.output(17,GPIO.HIGH)
        # query user to preview or start
        var = raw_input("[p]review, new [d]irectory, or [s]tart? (p/d/s): ")
        if (str(var) == 'p'):
            var_secs = raw_input("Preview time in seconds: ")
            picamPreview(int(var_secs))
        if (str(var) == 'd'):
            global new_target_dir
            new_target_dir = raw_input("Enter new directory name: ")
            if (str(new_target_dir).endswith('/') == 0):
                new_target_dir = new_target_dir+"/"
            if not os.path.isdir(new_target_dir):
                os.makedirs(new_target_dir)   
            print("     Files will be saved to "+new_target_dir+" for this session")
        if (str(var) == 's'):
            global var_fileheader  
            # create new unique filename
            var_fileheader = raw_input("Enter unique file name (e.g.: mouseB_day1): ")
            print("Camera ready...")
            print("Waiting for trigger...")
            GPIO.output(17,GPIO.LOW)
            break;
            #var_quit = raw_input("Press Ctrl+C to quit...")

## Begin script:
queryPreview()

while True:
    if(GPIO.input(24) ==1): # this would be the trigger input pin (may need to be ==0 depending on trigger input
        starttime = strftime("%Y-%m-%d %H:%M:%S")

        # Check to see if a custom directory (e.g., for USB drive) has been entered by user
        if 'new_target_dir' in globals():
            target_dir = new_target_dir

        # Check that file does not exist and if does, create unique tag to prevent overwrite
        unique_tag = "_"+strftime("%Y%m%d_%H%M%S")
        img_filename = "pic_"+var_fileheader+".jpg"
        if os.path.isfile(target_dir+img_filename):
                img_filename = "pic_"+var_fileheader+unique_tag+"_0.jpg"
        vid_filename = "vid_"+var_fileheader+".h264"
        if os.path.isfile(target_dir+vid_filename):
                vid_filename = "vid_"+var_fileheader+unique_tag+"_0.h264"
        mp4_filename = "vid_"+var_fileheader+".mp4"
        if os.path.isfile(target_dir+mp4_filename):
                mp4_filename = "vid_"+var_fileheader+unique_tag+"_0.mp4"
        
        iname=0
        
        print("     New filename: "+vid_filename)
        print("     Saving to    : "+target_dir)
        print("CAMERA RECORDING ... ")

        # Turn IR LEDs on
        GPIO.output(17,GPIO.HIGH) # LED
        
        picamVideo(starttime,vidfps)
        
        print("CAMERA OFF")
        # Turn IR LEDs off
        GPIO.output(17,GPIO.LOW) # LED

        print(" ")

        # Command line: Convert .h264 to mp4
        #print("     H264 to mp4 example: $ MP4Box -add "+vid_filename+" newvid.mp4")
        from subprocess import call
        mp4conversion = ("MP4Box -fps "+str(vidfps)+" -add "+target_dir+vid_filename+" "+target_dir+mp4_filename)
        call ([mp4conversion], shell=True)
        print(vid_filename+" converted to "+mp4_filename)

        queryPreview()
    
GPIO.cleanup()
