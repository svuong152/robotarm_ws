# Hướng dẫn chạy Code Robot Arm (ROS 2)

## 1. Cài đặt các thư viện cần thiết (Dependencies)
Nếu máy bạn mới cài ROS 2 Humble và chưa có các công cụ build hoặc thư viện MoveIt, hãy mở terminal và chạy lần lượt các lệnh sau:

```bash
# 1. Cập nhật hệ thống
sudo apt update

# 2. Cài đặt công cụ build (Colcon) và rosdep
sudo apt install python3-colcon-common-extensions python3-rosdep -y

# 3. Khởi tạo và cập nhật rosdep (Nếu máy bạn chưa từng chạy lệnh này)
sudo rosdep init
rosdep update

# 4. Cài đặt thư viện MoveIt 2 (phiên bản Humble)
sudo apt install ros-humble-moveit -y
```

---

## 2. Tải code và Build (Biên dịch)
Sau khi đã có đủ thư viện cơ bản, chạy các lệnh sau để tải workspace về và biên dịch:

```bash
# 1. Clone code từ GitHub về máy
git clone https://github.com/svuong152/robotarm_ws.git

# 2. Di chuyển vào thư mục workspace
cd robotarm_ws

# 3. Cập nhật lại apt để tránh lỗi thiếu gói phần mềm
sudo apt update

# 4. Dùng rosdep để tự động cài đặt các thư viện còn thiếu theo yêu cầu của code
rosdep install --from-paths src --ignore-src -r -y

# 5. Build toàn bộ code
colcon build

# 6. Nạp biến môi trường
source install/setup.bash
```


---

## 3. Hướng dẫn khởi chạy
Để điều khiển được robot, cần mở **2 Terminal** chạy song song:

### Terminal 1: Bật môi trường mô phỏng (RViz)
Mở terminal thứ nhất và gõ:
```bash
cd ~/robotarm_ws
source install/setup.bash
ros2 launch robotarm_moveit_config demo.launch.py
```
*(Đợi một lát cửa sổ RViz hiện lên hình cánh tay robot).*

### Terminal 2: Chạy file code điều khiển (ik_client)
Mở thêm một tab terminal mới và gõ:
```bash
cd ~/robotarm_ws
source install/setup.bash
ros2 run robotarm_control ik_client
```

---

## 4. Cách sử dụng Menu
Khi Terminal 2 chạy lên, màn hình sẽ hiện Menu điều khiển. Chỉ cần nhập phím tương ứng và nhấn Enter:

* **Nhập `0`:** Lệnh cho cánh tay tự động thu về vị trí Home mặc định.
* **Nhập `1`:** Chuyển sang chế độ nhập tọa độ. Lần lượt nhập vị trí X, Y, Z (đơn vị: mét) mà bạn muốn đầu gắp (tool0) đi tới. Hệ thống sẽ tự tính toán góc quay và di chuyển robot.
* **Nhập `q`:** Thoát chương trình.

---

## 5. Mẹo: In nhanh tọa độ hiện tại của đầu gắp (tool0)
Nếu trong quá trình chạy mà bạn muốn kiểm tra xem tọa độ không gian (X, Y, Z) và góc xoay hiện tại của đầu gắp (`tool0`) đang ở đâu, hãy mở một terminal mới và chạy lệnh sau:

```bash
ros2 run tf2_ros tf2_echo base_link tool0
```
* **Ý nghĩa:** Lệnh này sẽ liên tục lắng nghe hệ tọa độ của ROS 2 và in ra màn hình vị trí chính xác (Translation) cùng góc xoay (Rotation) của `tool0` so với gốc tọa độ `base_link` của robot theo thời gian thực.
* **Cách thoát:** Bấm tổ hợp phím `Ctrl + C` để dừng lại.
