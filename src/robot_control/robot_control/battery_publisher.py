import time
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from robot_interfaces.action import Recharge
from robot_interfaces.msg import RobotStatus


class BatteryAndRechargeNode(Node):

  def __init__(self):
    super().__init__('battery_and_recharge_node')

    # 1. Battery Publisher & State
    self.battery_pub = self.create_publisher(RobotStatus, 'battery_topic', 10)
    self.battery = 70.0
    self.is_charging = (
        False  # Flag to pause normal drain while charging is active
    )

    # 2. Action Server
    self._action_server = ActionServer(
        self, Recharge, 'recharge_robot_action', self.execute_callback
    )

    # 3. Timer for regular battery updates (every 1 second)
    self.create_timer(1.0, self.timer_callback)
    self.get_logger().info('Battery & Recharge Action Server Node is Running.')

  def timer_callback(self):
    # Only drain the battery if we aren't currently plugged in/charging via the action
    if not self.is_charging and self.battery > 0.0:
      self.battery -= 10.0

    msg = RobotStatus()
    msg.battery_level = self.battery
    msg.needs_charging = self.battery <= 20.0
    msg.status_message = f'Battery level : {msg.battery_level}%'

    self.battery_pub.publish(msg)
    self.get_logger().info(f'Battery level published: {self.battery}%')

  def execute_callback(self, goal_handle):
    self.get_logger().info('Executing recharge goal...')
    self.is_charging = True  # Pause normal timer drain

    target = goal_handle.request.target_battery_level
    feedback_msg = Recharge.Feedback()

    # Step-by-step charging loop
    while self.battery < target:
      self.battery += 10.0
      if self.battery > 100.0:
        self.battery = 100.0

      feedback_msg.current_battery_level = self.battery

      # Publish feedback to the client
      self.get_logger().info(f'Feedback: Charging... {self.battery}%')
      goal_handle.publish_feedback(feedback_msg)

      # Simulate a 1-second delay per 10% charge step
      time.sleep(1.0)

    # Resume normal battery status updates after charging finishes
    self.is_charging = False

    # Mark the action goal as succeeded
    goal_handle.succeed()

    result = Recharge.Result()
    result.success = True
    result.message = f'Successfully recharged to target level: {self.battery}%!'
    
    self.get_logger().info(result.message)
    return result


def main(args=None):
  rclpy.init(args=args)
  node = BatteryAndRechargeNode()
  rclpy.spin(node)
  rclpy.shutdown()


if __name__ == '__main__':
  main()