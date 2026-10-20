import rclpy
from rclpy.node import Node
from robot_interfaces.msg import RobotStatus

class sub_node(Node):
    def __init__(self):
        super().__init__("battery_status_sub")
        self.get_logger().info("Battery Sub Node is runing")
        self.battery_sub = self.create_subscription(RobotStatus, "battery_topic" , self.battery_sub_callback , 10 )

    def battery_sub_callback (self, msg):
        if msg.needs_charging == True:
            self.get_logger().info("Robot needs charging")
        else:
            self.get_logger().info(f"Battery level: {msg.battery_level}%")

def main():
    rclpy.init()
    node = sub_node()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
