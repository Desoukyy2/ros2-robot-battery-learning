import rclpy
from rclpy.node import Node
from robot_interfaces.srv import RechargeRobot
from robot_interfaces.msg import RobotStatus


class client_node(Node):

    def __init__(self):
        super().__init__("recharge_client_node")
        self.recharge_client = self.create_client(RechargeRobot , "recharge_robot")
        while not self.recharge_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for server")
        self.subscription = self.create_subscription(
        RobotStatus, 'battery_topic', self.battery_callback, 10
    )
        self.recharge_requested = False


    def battery_callback(self, msg):
        self.get_logger().info(f'Current Battery: {msg.battery_level}%')

        # If battery drops below 20% and we haven't requested a recharge yet:
        if msg.needs_charging and not self.recharge_requested:
            self.get_logger().info('Battery low! Automatically requesting recharge...')
            self.send_request(50.0)
            self.recharge_requested = (
                True  # Lock it so it doesn't spam requests every second
            )

    def send_request (self , amount):
        req = RechargeRobot.Request()
        req.charge_amount = amount
        self.future = self.recharge_client.call_async(req)
        self.future.add_done_callback(self.handle_response)

    def handle_response(self, future):
        response = future.result()  # Here is your actual response object!
        self.get_logger().info(
          f'Server response -> Success: {response.success}, Message:'
          f' {response.message}')

        if response.success:
            self.recharge_requested = False

        
def main():
    rclpy.init()
    node = client_node()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()