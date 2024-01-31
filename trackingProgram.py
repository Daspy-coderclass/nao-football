# -*- encoding: UTF-8 -*-

"""
This example shows how to use ALTracker with red ball.
"""

import math
import time
import argparse
from naoqi import ALProxy

IP = "192.168.5.29"  # Replace here with your NaoQi's IP address.
PORT = 9559

print ("Connecting to", IP, "with port", PORT)
memoryProxy = ALProxy("ALMemory", IP, PORT)
motion = ALProxy("ALMotion", IP, PORT)
posture = ALProxy("ALRobotPosture", IP, PORT)
tracker = ALProxy("ALTracker", IP, PORT)
camera = ALProxy("ALVideoDevice", IP, PORT)
landMarkProxy = ALProxy("ALLandMarkDetection", IP, PORT)

targetName = "RedBall"
diameterOfBall = 0.06
memValue = "LandmarkDetected"

def landmarkDetection(): #Return True als je een landmark ziet
    time.sleep(0.1)
    landmarkValue = memoryProxy.getData(memValue) #haal de waarde op van het event "LandmarkDetected"
    if(landmarkValue and isinstance(landmarkValue, list) and len(landmarkValue) >= 2): #controleer of je landmarks ziet en of er een lijst wordt meegegeven
        markInfoArray = landmarkValue[1]
        try:
            for markInfo in markInfoArray:
                print "mark  ID: %d" % (markInfo[1][0])
                return True 
        except Exception, e:
            print "Naomarks detected, but it seems getData is invalid. ALValue ="
            print landmarkValue
            print "Error msg %s" % (str(e))

def main(IP, PORT, ballSize):
    motion.wakeUp()
    camera.setActiveCamera(1) #Schakel naar onderste camera

    fractionMaxSpeed = 0.8
    posture.goToPosture("StandInit", fractionMaxSpeed)

    def Rondje_om_bal():
        camera.setActiveCamera(0) #wissel naar bovenste camera om landmarks te kunnen zien
        period = 500
        landMarkProxy.subscribe("Test_LandMark", period, 0.0) #Begin landmark detectie
        time.sleep(0.3)
        for i in range(30):
            motion.setAngles("HeadPitch", 0.0,0.1) #kijk rechtvooruit
            motion.setAngles("HeadYaw", 0.0,0.1)
            time.sleep(0.3) #pauze
            motion.post.moveTo(0.3,-0.3,(math.pi/2)) #begin met 25% van een circkel te lopen
            print("Begin move "+str(1+i))
            while motion.moveIsActive(): #check tijdens het lopen of je een landmark ziet
                if landmarkDetection():
                    landMarkProxy.unsubscribe("Test_LandMark") #stop landmark detectie
                    print "Ga nu lopen"
                    return True
            motion.waitUntilMoveIsFinished() 

    def lopen_naar_bal(stopDistance):
        tracker.registerTarget(targetName, diameterOfBall) #maak rode ball een target
        tracker.setMode("Move")
        tracker.track(targetName) #begin met tracken
        print "ALTracker successfully started, now show a red ball to robot!"
        print "Use Ctrl+c to stop this script."
        while True:
            xyz_distance = tracker.getTargetPosition(2) #haal positie rode bal op
            if str(xyz_distance) != "[]": #kijk of er een rode bal wordt gespot
                if float(xyz_distance[0]) <= stopDistance: #Als de bal in 30 cm is, stop met tracken
                    print(xyz_distance)
                    tracker.stopTracker()
                    return True
    
    def lopen_naar_landmark():
        print("In lopen_naar_landmark")
        motion.moveTo(0.6,0,0) #loop 60cm naar voren, hopelijk richting de landmark


    try:
        volgende = False
        volgende = lopen_naar_bal(0.3)
        if volgende:
            if Rondje_om_bal():
                lopen_naar_landmark()
                print("klaar met programma")
    
    except KeyboardInterrupt:
        tracker.unregisterAllTargets()
        if volgende:
            landMarkProxy.unsubscribe("Test_LandMark")
        motion.rest()
        exit(1)
        print "Interrupted by user"
        print "Stopping..."

    # Stop tracker, go to posture Sit.
    tracker.stopTracker()
    tracker.unregisterAllTargets()
    motion.rest()
    print "ALTracker stopped."
    print "Landmark proxy stopped"


if __name__ == "__main__" :

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=IP,
                        help="Robot ip address.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Robot port number.")
    parser.add_argument("--ballsize", type=float, default=0.06,
                        help="Diameter of ball.")

    args = parser.parse_args()

    main(args.ip, args.port, args.ballsize)