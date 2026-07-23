from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_share = get_package_share_directory(
        'robotarm_description'
    )

    urdf_file = os.path.join(
        pkg_share,
        'urdf',
        'robotarm.urdf.xacro'
    )

    robot_description = {
        'robot_description': Command(
            ['xacro ', urdf_file]
        )
    }

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[robot_description],
            output='screen'
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            output='screen'
        ),
    ])
