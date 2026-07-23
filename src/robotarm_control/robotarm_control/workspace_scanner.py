#!/usr/bin/env python3

import rclpy
import math
from rclpy.node import Node
from moveit_msgs.srv import GetPositionIK
from geometry_msgs.msg import PoseStamped
from builtin_interfaces.msg import Duration

class WorkspaceScanner(Node):

    def __init__(self):
        super().__init__('workspace_scanner')
        self.cli = self.create_client(GetPositionIK, '/compute_ik')
        
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /compute_ik ...')
            
        self.joint_names = [
            "joint_1", "joint_2", "joint_3", 
            "joint_4", "joint_5", "joint_6"
        ]

    def euler_to_quaternion(self, roll, pitch, yaw):
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)

        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy
        qw = cr * cp * cy + sr * sp * sy
        return qx, qy, qz, qw

    # Hàm tạo mảng số thập phân
    def frange(self, start, stop, step):
        i = start
        while i <= stop:
            yield round(i, 3)
            i += step

    def scan_workspace(self):
        req = GetPositionIK.Request()
        req.ik_request.group_name = "robotarm"
        req.ik_request.ik_link_name = "tool0"
        req.ik_request.robot_state.joint_state.name = self.joint_names
        req.ik_request.robot_state.joint_state.position = [
            0.0, math.radians(45), math.radians(-90), math.radians(-45), math.radians(90), 0.0
        ]
        
        # Đặt timeout siêu ngắn để quét cho nhanh
        req.ik_request.timeout = Duration(sec=0, nanosec=50000000) 

        pose = PoseStamped()
        pose.header.frame_id = "base_link"

        reachable_points = []

        print("[INFO] Đang quét không gian 3D. Quá trình này có thể mất vài phút...")
        
        # Thiết lập vùng quét: X, Y từ -0.5m đến 0.5m, Z từ 0.0m đến 0.6m. Bước nhảy 10cm.
        for x in self.frange(-0.5, 0.5, 0.1):
            for y in self.frange(-0.5, 0.5, 0.1):
                for z in self.frange(0.0, 0.6, 0.1):
                    
                    pose.pose.position.x = x
                    pose.pose.position.y = y
                    pose.pose.position.z = z
                    
                    success = False
                    
                    # Quét góc Roll như thuật toán cũ (Bước nhảy 30 độ cho nhanh)
                    for roll_deg in range(-180, 181, 30):
                        qx, qy, qz, qw = self.euler_to_quaternion(math.radians(roll_deg), 0.0, 0.0)
                        pose.pose.orientation.x = qx
                        pose.pose.orientation.y = qy
                        pose.pose.orientation.z = qz
                        pose.pose.orientation.w = qw
                        
                        req.ik_request.pose_stamped = pose
                        
                        future = self.cli.call_async(req)
                        rclpy.spin_until_future_complete(self, future)
                        result = future.result()

                        if result is not None and result.error_code.val == 1:
                            success = True
                            break # Tìm được 1 góc Roll khả thi là đủ, sang tọa độ tiếp theo
                    
                    if success:
                        print("ok, đã quét dc 1 tọa độ")
                        reachable_points.append(f"{x}, {y}, {z}\n")

        # Ghi kết quả ra file
        with open("reachable_workspace.txt", "w") as f:
            f.writelines(reachable_points)
            
        print(f"\n[HOÀN THÀNH] Đã tìm được {len(reachable_points)} tọa độ khả thi!")
        print("Kết quả được lưu tại file: reachable_workspace.txt (trong thư mục ông đang chạy lệnh)")

def main():
    rclpy.init()
    node = WorkspaceScanner()
    node.scan_workspace()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
