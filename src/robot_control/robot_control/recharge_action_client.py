import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from robot_interfaces.msg import RobotStatus
from robot_interfaces.action import Recharge

class  RechargeActionClient(Node):

    def __init__(self):
       super().__init__('recharge_action_client')
       self._action_client = ActionClient(self , Recharge , 'recharge_robot_action' )
       while not self._action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info("Waiting for actionserver")

       self.subscription = self.create_subscription(
               RobotStatus, 'battery_topic', self.battery_callback, 10
           )
       self.recharge_requested = False

    def send_goal(self , target_value):
      req = Recharge.Goal()
      req.target_battery_level = target_value
      self.future = self._action_client.send_goal_async(req ,feedback_callback=self.feedback_callback )
      self.future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
      feedback = feedback_msg.feedback
      self.get_logger().info(
          f'Feedback received -> Current Battery Level: {feedback.current_battery_level}%'
      )

    def goal_response_callback(self , future):
       goal_handle = future.result()
       if not goal_handle.accepted:
          self.get_logger().info("Goal rejected")
          return

       self.get_logger().info('Goal accepted')

       self.get_result_future = goal_handle.get_result_async()
       self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self , future):
       result_wrapper = future.result()
       result = result_wrapper.result
       self.get_logger().info(
         f'Result received -> Success: {result.success}, Message: {result.message}'
     )
       self.recharge_requested = False

    def battery_callback(self, msg):
            self.get_logger().info(f'Current Battery: {msg.battery_level}%')
    
            # If battery drops below 20% and we haven't requested a recharge yet:
            if msg.needs_charging and not self.recharge_requested:
                self.get_logger().info('Battery low! Automatically requesting recharge...')
                self.send_goal(100.0)
                self.recharge_requested = (
                    True  # Lock it so it doesn't spam requests every second
                )
            

def main(args=None):
  rclpy.init(args=args)
  node = RechargeActionClient()
  rclpy.spin(node)
  rclpy.shutdown()


if __name__ == '__main__':
  main()
   