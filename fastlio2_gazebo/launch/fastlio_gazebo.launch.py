import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 获取Gazebo启动文件路径
    gazebo_launch_dir = os.path.join(
        get_package_share_directory('gazebo_ros'), 'launch'
    )
    
    # 获取模型和世界文件路径
    fastlio_gazebo_dir = os.path.join(
        get_package_share_directory('fastlio2_gazebo'),
        'worlds'
    )
    
    # 启动Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_launch_dir, 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(fastlio_gazebo_dir, 'fastlio_world.world'),
            'verbose': 'true'
        }.items(),
    )
    
    # 启动joint_state_publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )
    
    # 启动机器人状态发布器
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': open(
                os.path.join(
                    get_package_share_directory('fastlio2_gazebo'),
                    'models', 'fastlio_robot', 'fastlio_robot.urdf'
                ), 'r').read()
        }]
    )
    
    # 启动spawn_entity节点，将机器人模型加载到Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'fastlio_robot',
            '-file', os.path.join(
                get_package_share_directory('fastlio2_gazebo'),
                'models', 'fastlio_robot', 'fastlio_robot.urdf'
            ),
            '-x', '0',
            '-y', '0',
            '-z', '0.3'
        ],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        spawn_entity
    ])