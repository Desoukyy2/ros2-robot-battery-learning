import rclpy
from rclpy.node import Node
from robot_interfaces.srv import RechargeRobot
from robot_interfaces.msg import RechargeRequest

from std_msgs.msg import Float32

class recharge_node(Node):

    def __init__(self):
        super().__init__("recharge_server_node")
        self.recharge_robot =self.create_service(RechargeRobot ,"recharge_robot" , self.recharge_callback )
        self.recharge_pub = self.create_publisher(RechargeRequest , "recharge_amount" , 10)

    def recharge_callback (self , request , response):
        self.get_logger().info(f"Charge amount :{request.charge_amount}")
        amount = request.charge_amount
        msg = RechargeRequest()
        msg.recharge_amount = amount
        self.recharge_pub.publish(msg)
        response.success = True
        response.message = "Recahrge complete!"
        
        return response


def main():
    rclpy.init()
    node = recharge_node()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()