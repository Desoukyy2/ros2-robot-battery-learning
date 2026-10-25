import rclpy
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from rclpy.node import Node
from robot_interfaces.msg import RobotStatus
from robot_interfaces.action import Recharge
from std_srvs.srv import Trigger

class  RechargeActionClient(Node):

    def __init__(self):
       super().__init__('recharge_action_client')
       self._action_client = ActionClient(self , Recharge , 'recharge_robot_action' )
       while not self._action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info("Waiting for action server")
       self.cancel_recharge = self.create_service(Trigger , 'cancel_recharge' , self.cancel_recharge_callback)
       self.resume_recharge = self.create_service(Trigger , 'resume_recharge' , self.resume_recharge_callback)
       self.subscription = self.create_subscription(
               RobotStatus, 'battery_topic', self.battery_callback, 10
           )
       self.recharge_requested = False
       self.auto_recharge_paused = False
       self.goal_handle = None

    def send_goal(self , target_value):
      req = Recharge.Goal()
      req.target_battery_level = target_value
      self.future = self._action_client.send_goal_async(req ,feedback_callback=self.feedback_callback )
      self.future.add_done_callback(self.goal_response_callback)

    def cancel_recharge_callback(self , request , response ):
       if self.goal_handle is None:
          response.success = False
          response.message = 'No active recharge goal to cancel'
          self.get_logger().info(response.message)
       else:
         self.cancel_request()
         response.success = True
         response.message = 'Cancellation request has been submitted'

       return response

    def resume_recharge_callback(self , request , response ):
            self.resume_request()
            response.success = True
            response.message = 'Automatic recharging has been resumed'
            self.get_logger().info(response.message)
            return response

    def resume_request(self):
          self.get_logger().info('Requesting auto charging resume request')
          self.auto_recharge_paused = False

    def feedback_callback(self, feedback_msg):
      feedback = feedback_msg.feedback
      self.get_logger().info(
          f'Feedback received -> Current Battery Level: {feedback.current_battery_level}%'
      )

    def goal_response_callback(self , future):
       goal_handle = future.result()
       if not goal_handle.accepted:
          self.get_logger().info("Goal rejected")
          self.recharge_requested = False
          return

       self.get_logger().info('Goal accepted')

       self.goal_handle = goal_handle

       self.get_result_future = goal_handle.get_result_async()
       self.get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self , future):
       result_wrapper = future.result()
       result = result_wrapper.result
       if result_wrapper.status == GoalStatus.STATUS_CANCELED:
          self.auto_recharge_paused = True
       self.get_logger().info(
         f'Result received -> {result.success}, Message: {result.message}'
     )
       self.recharge_requested = False
       self.goal_handle = None

    def battery_callback(self, msg):
            self.get_logger().info(f'Current Battery: {msg.battery_level}%')
    
            # If battery drops below 20% and we haven't requested a recharge yet:
            if msg.needs_charging and not self.recharge_requested and not self.auto_recharge_paused:
                self.get_logger().info('Battery low! Automatically requesting recharge...')
                self.send_goal(100.0)
                self.recharge_requested = (
                    True  # Lock it so it doesn't spam requests every second
                )
    def cancel_request(self):
       if self.goal_handle is not None:
          self.get_logger().info('Requesting Cancelation')
          cancel_future = self.goal_handle.cancel_goal_async()
          cancel_future.add_done_callback(self.cancel_response_callback)
       else :
          self.get_logger().info('Could not request cancelation (No recharge requested)')


    def cancel_response_callback(self , future):
       response = future.result()

       if response.goals_canceling:
            self.get_logger().info('Cancelation Request Accepted')
       else:
            self.get_logger().info('Cancelation Request is not Accepted')
              
       

def main(args=None):
  rclpy.init(args=args)
  node = RechargeActionClient()
  rclpy.spin(node)
  rclpy.shutdown()


if __name__ == '__main__':
  main()
   