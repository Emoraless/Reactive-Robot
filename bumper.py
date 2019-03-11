import rospy
import random
from kobuki_msgs.msg import BumperEvent
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
import math

#This is used for laser detection
laserDetectCounter = 0

#Used for changing angle when the laser detects somthing
angleMove = 0.0
# To check the distance
counter = 0
# Control the distance to reverse
rev_counter = 0
# Determines if there is a bump
bump = False
laser_detection = False
sym = False
# 0 = neutral
# 1 = left
# 2 = right
direction = 0
rightDetection = False
leftDetection = False

def processBump(data):
    global bump
    if (data.state == BumperEvent.PRESSED):
        bump = True
    # else:
        # bump = False
    rospy.loginfo("Bumper Event")
    rospy.loginfo(data.bumper)



#Used for laser detection
def callbackLaser(data):
    global laser_detection
    global laserDetectCounter
    global sym
    global direction
    #print len(msg.ranges)
    #print data.ranges
    value = 100
    #print "Center"
    center = data.ranges[320]
    print center
    right = data.ranges[320-value]
    left = data.ranges[320+value]
    #print "Right"
    print right
    #print "Left"
    print left

    #Checks to see if it hits the center laser
    if(center <= 0.3 and round(right, 0.3) == round(left, 1)):
        rospy.loginfo("Cener Found TURN AROUND 180")
        laser_detection = True
        sym = True
        direction = 0
        # This goes 180

    elif(center <= 0.3 and round(right, 0.3) > round(left, 1)):
        rospy.loginfo("Cener Found TURN AROUND 45 left")
        laser_detection = True
        sym = False
        direction = 2
        #Alter 45 degrees left

    elif(center <= 0.3 and round(right, 0.3) < round(left, 1)):
        rospy.loginfo("Cener Found TURN AROUND 45 right")
        laser_detection = True
        sym = False
        direction = 1
        #Alter 45 degrees right




    else: #handles if it is getting nan as a return
        laser_detection = False
        rospy.loginfo("TEST")
        #Change the rotation back to how it was origionaly
        angleMove = 0.0



#This is used for getting user input
def callback(data):
    if(data.data != ""):
        rospy.loginfo("%s", data.data)


def GoForward():
    global counter
    global bump
    global rev_counter
    # initiliaze
    rospy.init_node('GoForward', anonymous=False)

    # tell user how to stop TurtleBot
    rospy.loginfo("To stop TurtleBot CTRL + C")

    # What function to call when you ctrl + c
    rospy.on_shutdown(shutdown)
    # Create a publisher which can "talk" to TurtleBot and tell it to move
    cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
    # Create subscriber to the bumper to detect when there is a collision
    sub = rospy.Subscriber('mobile_base/events/bumper', BumperEvent, processBump)
    #Subscriber used for the laser
    subLaser = rospy.Subscriber("scan", LaserScan, callbackLaser)
    #Used to get user information
    rospy.Subscriber("chatter", String, callback)

    #TurtleBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
    r = rospy.Rate(10)

    # Twist is a datatype for velocity
    # For forward movement
    move_cmd = Twist()
    # let's go forward at 0.2 m/s
    move_cmd.linear.x = 0.2
    # let's turn at 0 radians/s
    move_cmd.angular.z = 0.0

    # To reverse after the collision
    reverse_cmd = Twist()
    # let's go backwards at 0.2 m/s
    reverse_cmd.linear.x = -0.2
    # let's turn at 0 radians/s
    reverse_cmd.angular.z = 0.0

    # To halt after the collision occured
    halt_cmd = Twist()
    # let's go backwards at 0.2 m/s
    halt_cmd.linear.x = 0.0
    # let's turn at 0 radians/s
    halt_cmd.angular.z = 0.0

    # To halt after the collision occured
    turn_cmd = Twist()
    # let's go backwards at 0.2 m/s
    turn_cmd.linear.x = 0.0
    # let's turn at 0 radians/s
    turn_cmd.angular.z = 0.2

    # To halt after the collision occured
    turn_left_cmd = Twist()
    # let's go backwards at 0.2 m/s
    turn_left_cmd.linear.x = 0.0
    # let's turn at 0 radians/s
    turn_left_cmd.angular.z = -0.2

    # as long as you haven't ctrl + c keeping doing...
    while not rospy.is_shutdown():
        # If not bump has occured
        if bump == False:
            if laser_detection == True:
                if sym == True:
                    randomValInt = random.randint(1,30)
                    # Determine if value is positive or negative for the degree
                    polar = random.randint(0,1)
                    # If positive
                    if polar == 0:
                        # Assign the degree to randomValInt
                        randomValInt = randomValInt + 180
                    # If negative
                    else:
                        # Assign the degree to randomValInt
                        randomValInt = -1*randomValInt + 180
                    relative_angle = randomValInt*2*3.1415926535897/360
                    current_angle = 0
                    t0 = rospy.Time.now().to_sec()
                    while (current_angle < relative_angle):
                        cmd_vel.publish(turn_cmd)
                        t1 = rospy.Time.now().to_sec()
                        current_angle = 0.2*(t1-t0)
                else:
                    if direction == 1: # left
                        relative_angle = 45*2*3.1415926535897/360
                        current_angle = 0
                        t0 = rospy.Time.now().to_sec()
                        while (current_angle < relative_angle):
                            cmd_vel.publish(turn_cmd)
                            t1 = rospy.Time.now().to_sec()
                            current_angle = 0.2*(t1-t0)
                    elif direction == 2:
                        relative_angle = 45*2*3.1415926535897/360
                        current_angle = 0
                        t0 = rospy.Time.now().to_sec()
                        while (current_angle < relative_angle):
                            cmd_vel.publish(turn_left_cmd)
                            t1 = rospy.Time.now().to_sec()
                            current_angle = 0.2*(t1-t0)
            else:

                laserDetectCounter = 0
                # Counter counts the amount of 0.1 seconds have occured.
                counter += 1
                # Traveling at 0.2 m/s for 1.5 seconds equal a foot of distance
                if counter % 15 == 0:
                    # Choose degree between 1-15
                    randomValInt = random.randint(1,15)
                    # Determine if value is positive or negative for the degree
                    polar = random.randint(0,1)
                    # If positive
                    if polar == 0:
                        # Assign the degree to randomValInt
                        randomValInt = randomValInt
                    # If negative
                    else:
                        # Assign the degree to randomValInt
                        randomValInt = -1*randomValInt
                    # Convert degrees to radian and assign to move_cmd.angular.z
                    move_cmd.angular.z = randomValInt*2*3.1415926535897/360 #0
                # publish the velocity
                cmd_vel.publish(move_cmd)
            # wait for 0.1 seconds (10 HZ) and publish again
            r.sleep()
        # If bump has occured, then turtlebot needs to halt
        else:

            # Keep track of the counter
            rev_counter += 1
            # Reverse to be able to remove the message of the bumper
            if rev_counter <= 6:
                cmd_vel.publish(reverse_cmd)
            # Halt the turtlebot
            else:
                cmd_vel.publish(halt_cmd)
            r.sleep()




def shutdown():
    cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
    # stop turtlebot
    rospy.loginfo("Stop TurtleBot")
    # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
    cmd_vel.publish(Twist())
    # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
    rospy.sleep(1)




if __name__ == '__main__':
    try:
        GoForward()
    except:
      rospy.loginfo("GoForward node terminated.")
