from naoqi import ALProxy, ALModule, ALBroker
import math
import time



if __name__ == "__main__":
    IP = "192.168.5.29"
    PORT = 9559  # Default port for NAOqi API
    motion = ALProxy("ALMotion", IP, PORT)
    try:
        motion.walkInit()
        for i in range(1):
            motion.post.moveTo(0,-0.2,(math.pi/2))
            motion.waitUntilMoveIsFinished()
            print(i)

    except Exception as e:
        print("Error:", e)
