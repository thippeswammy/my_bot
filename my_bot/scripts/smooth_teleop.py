#!/usr/bin/env python3
import sys
import termios
import tty
import select
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# Settings for sensitivity
LINEAR_MAX = 0.5   # m/s
ANGULAR_MAX = 1.0  # rad/s
LINEAR_STEP = 0.05
ANGULAR_STEP = 0.1
DECAY = 0.8        # Factor to decay speed when no key pressed (0.0-1.0)

msg = """
Control Your Robot!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease linear velocity (forward/backward)
a/d : increase/decrease angular velocity (left/right)
s   : force stop

CTRL-C to quit
"""

def getKey(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.01) 
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

class SmoothTeleop(Node):
    def __init__(self):
        super().__init__('smooth_teleop')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.target_linear = 0.0
        self.target_angular = 0.0
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.settings = termios.tcgetattr(sys.stdin)
        self.last_key_time = time.time()
        
        self.timer = self.create_timer(0.05, self.loop) # 20Hz control loop
        print(msg)

    def loop(self):
        try:
            key = getKey(self.settings)
            
            if key and len(key) > 0:
                self.last_key_time = time.time()
                if key == 'w':
                    self.target_linear = LINEAR_MAX
                elif key == 'x':
                    self.target_linear = -LINEAR_MAX
                elif key == 'a':
                    self.target_angular = ANGULAR_MAX
                elif key == 'd':
                    self.target_angular = -ANGULAR_MAX
                elif key == 's':
                    self.target_linear = 0.0
                    self.target_angular = 0.0
                elif key == '\x03': # Ctrl-C
                    raise KeyboardInterrupt
            
            # If no key pressed for a short duration, stop
            # This handles the gap between key repeats to avoid stuttering
            # If no key pressed for a short duration, decay speed
            # Use 0.5s timeout to handle slower key repeats or network lag
            if time.time() - self.last_key_time > 0.5:
                 self.target_linear = 0.0
                 self.target_angular = 0.0
                 # TODO: Could implement real decay here (e.g. self.target_linear *= DECAY)
                 # but for now, just increasing the timeout should fix the stuttering.


            twist = Twist()
            twist.linear.x = float(self.target_linear)
            twist.angular.z = float(self.target_angular)
            self.publisher_.publish(twist)

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            pass

    def stop(self):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.publisher_.publish(twist)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main(args=None):
    rclpy.init(args=args)
    teleop = SmoothTeleop()

    try:
        rclpy.spin(teleop)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        teleop.stop()
        teleop.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
