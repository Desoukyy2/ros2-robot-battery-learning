import rclpy
from rclpy.action import ActionServer, CancelResponse , GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from robot_interfaces.action import Recharge
from rclpy.executors import MultiThreadedExecutor
from robot_interfaces.msg import RobotStatus
import time


class BatteryAndRechargeNode(Node):

  def __init__(self):
    super().__init__('battery_and_recharge_node')

    # Inside your Node's __init__ method:
    self.declare_parameter('low_battery_threshold', 30.0)

    # 1. Battery Publisher & State
    self.battery_pub = self.create_publisher(RobotStatus, 'battery_topic', 10)
    self.battery = 70.0
    self.is_charging = (
        False  # Flag to pause normal drain while charging is active
    )

    self.action_callback_group = ReentrantCallbackGroup()


    # 2. Action Server
    self._action_server = ActionServer(
        self, Recharge, 'recharge_robot_action', 
        execute_callback= self.execute_callback , 
        goal_callback= self.goal_callback,
        cancel_callback=self.cancel_callback,
        callback_group=self.action_callback_group
    )

    # 3. Timer for regular battery updates (every 1 second)
    self.create_timer(1.0, self.timer_callback)
    self.get_logger().info('Battery & Recharge Action Server Node is Running.')

  def goal_callback(self , goal_request):
      goal = goal_request.target_battery_level
      if goal < 0 or goal > 100:
            return GoalResponse.REJECT
    
      return GoalResponse.ACCEPT
     


  def cancel_callback(self , cancel_request):
    self.get_logger().info('Received Cancel Request')
    return CancelResponse.ACCEPT


  def timer_callback(self):
    # Only drain the battery if we aren't currently plugged in/charging via the action
    if not self.is_charging and self.battery > 0.0:
      self.battery -= 10.0
    # Inside your node where you check the battery level:
    threshold = self.get_parameter('low_battery_threshold').value
    msg = RobotStatus()
    msg.battery_level = self.battery
    msg.needs_charging = self.battery <= threshold
    msg.status_message = f'Battery level : {msg.battery_level}%'

    self.battery_pub.publish(msg)

  def execute_callback(self, goal_handle):
    self.get_logger().info('Executing recharge goal...')
    target = goal_handle.request.target_battery_level
    if target < 0 or target > 100:
       goal_handle.abort()
       result = Recharge.Result()
       result.success = False
       result.message = f'Recharge request is aborted the target value must be between 0 and 100 '
       
       self.get_logger().info(result.message)
       return result
       

    self.is_charging = True
    feedback_msg = Recharge.Feedback()

    # Step-by-step charging loop
    while self.battery < target:

        # 1. Check whether cancellation was requested
        if goal_handle.is_cancel_requested:
            self.is_charging = False
            goal_handle.canceled()

            result = Recharge.Result()
            result.success = False
            result.message = f'Recharge canceled at {self.battery}%'

            self.get_logger().info(result.message)
            return result

        # 2. Increase the battery level
        self.battery += 10.0

        if self.battery > 100.0:
            self.battery = 100.0

        # 3. Publish feedback to the client
        feedback_msg.current_battery_level = self.battery
        goal_handle.publish_feedback(feedback_msg)

        # 4. Simulate charging time
        time.sleep(1.0)

    # Check cancellation again after the final charging step
    if goal_handle.is_cancel_requested:
        self.is_charging = False
        goal_handle.canceled()

        result = Recharge.Result()
        result.success = False
        result.message = f'Recharge canceled at {self.battery}%'

        self.get_logger().info(result.message)
        return result

    # 5. Charging completed successfully
    self.is_charging = False
    goal_handle.succeed()

    result = Recharge.Result()
    result.success = True
    result.message = (
        f'Successfully recharged to target level: {self.battery}%!'
    )

    self.get_logger().info(result.message)
    return result


def main(args=None):
  rclpy.init(args=args)
  node = BatteryAndRechargeNode()
  executor = MultiThreadedExecutor(num_threads=2)
  executor.add_node(node)
  executor.spin()
  rclpy.shutdown()


if __name__ == '__main__':
  main()