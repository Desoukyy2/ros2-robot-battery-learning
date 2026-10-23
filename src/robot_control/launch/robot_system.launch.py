from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    package_share_dir = get_package_share_directory('robot_control')
    config_file = os.path.join(
        package_share_dir, 'config', 'robot_params.yaml'
    )
    arg = DeclareLaunchArgument('low_battery_threshold' ,default_value='30.0')
    threshold = LaunchConfiguration('low_battery_threshold')
    threshold_value = ParameterValue(threshold , value_type=float)
    return LaunchDescription([
        arg,
        
         Node(
             package='robot_control',
             executable='battery_pub',
             output='screen',
            parameters=[config_file,{'low_battery_threshold': threshold_value}],
         ),

         Node(
              package='robot_control',
              executable='recharge_action_client',
              output='screen'  ,
         ),

    ])