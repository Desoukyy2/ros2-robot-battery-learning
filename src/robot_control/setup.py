from setuptools import find_packages, setup
import os 
from glob import glob


package_name = 'robot_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name , 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name , 'config'), glob('config/*.yaml')),
                ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kareem-saleh',
    maintainer_email='173469493+Desoukyy2@users.noreply.github.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [ 'run_node = robot_control.my_node:main',
                            'battery_pub = robot_control.battery_publisher:main',
                            'battery_sub = robot_control.battery_subscriber:main',
                            'recharge_server = robot_control.recharge_server:main',
                            'recharge_client = robot_control.recharge_client:main',
                            'recharge_action_client = robot_control.recharge_action_client:main'
        ],
    },
)
