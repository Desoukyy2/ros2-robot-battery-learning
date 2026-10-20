import rclpy
from rclpy.node import Node

class the_node(Node):
    def __init__ (self):
        super().__init__("my_first_node")
        self.get_logger().info("Hello ROS 2! My node is alive.")
        self.create_timer( 1.0 , self.timer_callback)

    def timer_callback(self):
        self.get_logger().info("Robot is running ")


def main():
    rclpy.init()
    node = the_node()
    rclpy.spin(node)
    rclpy.shutdown()

 
if __name__ == "__main__":
    main()