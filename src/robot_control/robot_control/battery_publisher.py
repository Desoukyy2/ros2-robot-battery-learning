import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot_interfaces.msg import RobotStatus
class battery_node(Node):
    def __init__(self):
        super().__init__("battery_status_Pub")
        self.get_logger().info("Battery Pub Node is Runing")
        self.battery_pub = self.create_publisher(RobotStatus,"battery_topic" ,10)
        self.create_timer(1.0 , self.battery_callback)

    def battery_callback(self):
        msg = RobotStatus()
        msg.battery_level = 20.0
        if msg.battery_level == 0.0:
            msg.needs_charging = True
        else :
            msg.needs_charging = False

        msg.status_message = f"Battery level : {msg.battery_level}%"
        self.battery_pub.publish(msg)
def main():
    rclpy.init()
    node = battery_node()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()

    