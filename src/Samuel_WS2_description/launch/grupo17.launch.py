"""Gazebo, RViz and the digit seven, ready for the group 17 recording."""
from os.path import join
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('Samuel_WS2_description')
    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(join(share, 'launch', 'gazebo.launch.py'))),
        Node(package='rviz2', executable='rviz2',
             arguments=['-d', join(share, 'config', 'trayectoria.rviz')],
             parameters=[{'use_sim_time': True}]),
        TimerAction(period=20., actions=[
            Node(package='Samuel_WS2_description', executable='trayectoria',
                 output='screen', parameters=[{'grupo': 17, 'use_sim_time': True}])
        ]),
    ])
