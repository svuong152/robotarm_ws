#!/usr/bin/env python3

import rclpy
import math
from rclpy.node import Node

from moveit_msgs.srv import GetPositionIK
from geometry_msgs.msg import PoseStamped
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class IKClient(Node):

    def __init__(self):
        super().__init__('ik_client')
        
        self.cli = self.create_client(GetPositionIK, '/compute_ik')
        
        self.traj_pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /compute_ik ...')
            
        self.joint_names = [
            "joint_1", "joint_2", "joint_3", 
            "joint_4", "joint_5", "joint_6"
        ]

    def go_home(self):
        # Đổi độ sang Radian để gửi cho ROS 2
        home_positions = [
            math.radians(0), 
            math.radians(45), 
            math.radians(-90), 
            math.radians(-45), 
            math.radians(90), 
            math.radians(0)
        ]
        
        traj_msg = JointTrajectory()
        traj_msg.joint_names = self.joint_names
        
        point = JointTrajectoryPoint()
        point.positions = home_positions
        point.time_from_start.sec = 2  # Cho robot 2 giây để lướt về Home cho mượt
        
        traj_msg.points.append(point)
        self.traj_pub.publish(traj_msg)
        
        print("\n[INFO] Đã gửi lệnh đưa robot về vị trí Home (0°, 45°, -90°, -45°, 90°, 0°)!")

    def solve_ik(self, px, py, pz):

        req = GetPositionIK.Request()
        req.ik_request.group_name = "robotarm"
        req.ik_request.ik_link_name = "tool0"
        
        req.ik_request.robot_state.joint_state.name = self.joint_names
        
        # Dùng luôn tư thế Home làm điểm xuất phát (Seed state) để tính toán IK tốt hơn
        req.ik_request.robot_state.joint_state.position = [
            0.0, math.radians(45), math.radians(-90), math.radians(-45), math.radians(90), 0.0
        ]

        pose = PoseStamped()
        pose.header.frame_id = "base_link"
        pose.pose.position.x = px
        pose.pose.position.y = py
        pose.pose.position.z = pz

        # Góc xoay tạm thời để 0,0,0,1 nhưng MoveIt sẽ bỏ qua nhờ position_only_ik: True
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = 0.0
        pose.pose.orientation.w = 1.0

        req.ik_request.pose_stamped = pose
        req.ik_request.timeout = Duration(sec=2, nanosec=0)

        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        result = future.result()

        if result is None:
            print("Service call failed")
            return

        if result.error_code.val != 1:
            print("\n[LỖI] IK failed! Không thể với tới tọa độ này.")
            print("Error code:", result.error_code.val)
            return

        print("\n=== KẾT QUẢ GÓC QUAY (ĐỘ) ===")
        for name, pos in zip(
            result.solution.joint_state.name,
            result.solution.joint_state.position
        ):
            deg = math.degrees(pos)
            print(f"{name}: {deg:.2f}°")

        # --- GỬI LỆNH ĐIỀU KHIỂN (ACTION) ---
        traj_msg = JointTrajectory()
        traj_msg.joint_names = result.solution.joint_state.name
        
        point = JointTrajectoryPoint()
        point.positions = result.solution.joint_state.position
        point.time_from_start.sec = 1  # Chạy tới điểm IK trong 1 giây
        
        traj_msg.points.append(point)
        
        self.traj_pub.publish(traj_msg)
        
        print("\n[INFO] Đã gửi lệnh quỹ đạo xuống /arm_controller/joint_trajectory !")

def main():
    rclpy.init()
    node = IKClient()

    # Vòng lặp vô hạn giữ cho file chạy liên tục
    while rclpy.ok():
        print("\n==================================")
        print("CHỌN CHẾ ĐỘ ĐIỀU KHIỂN:")
        print("  [0] - Quay về Home (0°, 45°, -90°, -45°, 90°, 0°)")
        print("  [1] - Nhập tọa độ đầu gắp (X, Y, Z)")
        print("  [q] - Thoát chương trình")
        print("==================================")
        
        choice = input("Lựa chọn của bạn: ").strip()
        
        if choice == '0':
            node.go_home()
        elif choice == '1':
            try:
                print("--- Nhập tọa độ (m) ---")
                px = float(input("X: "))
                py = float(input("Y: "))
                pz = float(input("Z: "))
                node.solve_ik(px, py, pz)
            except ValueError:
                print("[LỖI] Bạn phải nhập số! Vui lòng thử lại.")
        elif choice.lower() == 'q':
            print("Đang thoát chương trình...")
            break
        else:
            print("[LỖI] Lựa chọn không hợp lệ, vui lòng nhập lại!")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
