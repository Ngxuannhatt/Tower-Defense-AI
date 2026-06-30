import math
import random
import time
import path_step_monitor
from algorithms import astar

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    1. ỨNG DỤNG TÌM ĐƯỜNG: Giải thuật Simulated Annealing (Luyện kim giả lập).
    - Là thuật toán tối ưu hóa tìm kiếm cục bộ lấy cảm hứng từ quá trình luyện kim.
    - Tại mỗi bước, chọn ngẫu nhiên một ô hàng xóm lân cận (Random Neighbor).
    - Tính mức chênh lệch Delta = h(next_state) - h(current_state).
    - Nếu ô mới tốt hơn (gần đích hơn, Delta < 0), chấp nhận di chuyển ngay lập tức.
    - Nếu ô mới tệ hơn (xa đích hơn, Delta >= 0), chấp nhận di chuyển với xác suất Boltzmann p = e^(-Delta/T).
    - Việc chấp nhận nước đi tệ hơn giúp thuật toán có khả năng thoát khỏi các bẫy ngõ cụt (cực trị cục bộ).
    - Nhiệt độ T giảm dần theo hệ số hạ nhiệt alpha. Khi T lạnh đi, thuật toán sẽ ít chấp nhận đi lùi và tiến dần về đích.
    """
    path_step_monitor.log_step(f"Khởi chạy Simulated Annealing từ {start} đến {goal}")
    
    current = start
    path = [current]
    
    # Khởi tạo các tham số theo mã giả (T = T0)
    T = 100.0
    T_min = 0.01
    alpha = 0.95
    max_steps = 5000
    steps = 0
    
    # Định nghĩa hàm đánh giá Heuristic h(x) - Khoảng cách Manhattan đến đích
    def h(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    # Vòng lặp chính: while T > Tmin
    while T > T_min and steps < max_steps:
        steps += 1
        x, y = current
        
        # Nếu đã đạt tới đích, kết thúc
        if current == goal:
            break
            
        path_step_monitor.log_node_state(x, y, "closed")
        if delay > 0:
            time.sleep(delay)
            
        # Lấy tất cả các ô hàng xóm hợp lệ xung quanh ô hiện tại
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
                neighbors.append((nx, ny))
                
        if not neighbors:
            path_step_monitor.log_step(f"Bị kẹt tại {current} vì không có hàng xóm hợp lệ!")
            break
            
        # 1. Chọn NGẪU NHIÊN một ô hàng xóm (RandomNeighbor)
        next_state = random.choice(neighbors)
        
        # 2. Tính Delta = h(next_state) - h(current_state)
        # Vì bài toán tìm đường là bài toán TÌM MIN (khoảng cách h càng nhỏ càng tốt)
        delta = h(next_state) - h(current)
        
        # 3. Nếu ô tiếp theo tốt hơn (delta < 0) -> Chấp nhận di chuyển
        if delta < 0:
            current = next_state
            path.append(current)
            path_step_monitor.log_step(f"🌡️ T={T:.1f} | Chấp nhận ô tốt hơn: {current} (h={h(current)})")
        # 4. Ngược lại nếu ô tiếp theo tệ hơn -> Xét xác suất Boltzmann để quyết định đi lùi hay đứng yên
        else:
            p = math.exp(-delta / max(T, 0.01))
            if random.random() < p:
                current = next_state
                path.append(current)
                path_step_monitor.log_step(f"🎲 T={T:.1f} | Chấp nhận ô tệ hơn: {current} với p={p:.2f}")
            else:
                path_step_monitor.log_step(f"❌ T={T:.1f} | Từ chối ô tệ hơn: {next_state}. Đứng yên tại {current}")
                # Khi từ chối, current giữ nguyên, thuật toán đứng yên tại chỗ để vòng sau tìm hàng xóm khác
        
        path_step_monitor.log_node_state(current[0], current[1], "open")
        
        # 5. Hạ nhiệt độ sau mỗi bước thử
        T = max(T_min, T * alpha)
        
    if current == goal:
        path_step_monitor.log_step(f"Simulated Annealing đã đến đích thành công!")
        for px, py in path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return path
        
    path_step_monitor.log_step("Không tìm thấy đường đi tới đích hoặc hết nhiệt độ!")
    return None


def get_map_energy(map_manager) -> float:
    """
    Tính toán năng lượng dựa trên độ dài đường đi ngắn nhất của A*.
    - Đây là hàm đánh giá chất lượng của cách đặt tháp (Map Layout).
    - Năng lượng = -len(path). Độ dài đường đi càng dài (quái đi vòng lâu), năng lượng càng nhỏ/tốt.
    - Nếu đường đi bị chặn hoàn toàn (path is None), phạt nặng bằng mức năng lượng 999.0 để loại bỏ.
    """
    path = astar.solve(map_manager.start, map_manager.goal, map_manager, delay=0.0)
    if path is None:
        return 999.0  # Phạt nặng cấu hình chặn đường đi
    return -len(path)


def get_random_neighbor_layout(map_manager, num_towers):
    """
    Tạo cấu hình lân cận ngẫu nhiên bằng cách dịch chuyển 1 tháp sang ô trống mới.
    - Thu thập toàn bộ tọa độ ô trống và hợp lệ.
    - Chọn ngẫu nhiên một tháp hiện có, gỡ bỏ nó.
    - Chọn ngẫu nhiên một ô trống mới và đặt tháp đó vào.
    """
    # Lấy danh sách tất cả các tọa độ trống và hợp lệ trên bản đồ
    empty_cells = []
    for x in range(map_manager.width):
        for y in range(map_manager.height):
            if (x, y) != map_manager.start and (x, y) != map_manager.goal and (x, y) not in map_manager.towers:
                empty_cells.append((x, y))
                
    if not empty_cells:
        return # Bản đồ đã kín, không thể đổi vị trí tháp
        
    # Chọn ngẫu nhiên 1 tháp đang có để dịch chuyển sang 1 ô trống ngẫu nhiên
    if map_manager.towers:
        old_pos = random.choice(list(map_manager.towers.keys()))
        t_type = map_manager.towers[old_pos]
        map_manager.remove_tower(old_pos[0], old_pos[1])
        
        new_pos = random.choice(empty_cells)
        map_manager.add_tower(new_pos[0], new_pos[1], t_type)


def run_annealing(map_manager, num_towers, steps=80, log_callback=None, update_ui_callback=None):
    """
    2. ỨNG DỤNG TỐI ƯU HÓA MẠNG LƯỚI THÁP (Mê cung tháp):
    - Tối ưu hóa vị trí các tháp thủ thành bằng Simulated Annealing.
    - Khởi tạo: Đặt tháp ngẫu nhiên an toàn (không chặn đường đi).
    - Ở mỗi vòng lặp, di chuyển ngẫu nhiên một tháp (tạo trạng thái lân cận).
    - Tính Delta = next_energy - current_energy.
    - Nếu cấu hình mới tốt hơn (quái đi vòng dài hơn, Delta < 0), chấp nhận ngay.
    - Nếu cấu hình mới tệ hơn (Delta >= 0), chấp nhận với xác suất Boltzmann e^(-Delta/T).
    - Tự động hạ nhiệt độ T theo hệ số alpha để đảm bảo hội tụ sau đúng số bước 'steps'.
    """
    map_manager.reset()
    types = ["Basic", "Ice", "Fire"]
    
    # Thu thập toàn bộ ô trống để rải tháp ban đầu an toàn
    empty_cells = []
    for x in range(map_manager.width):
        for y in range(map_manager.height):
            if (x, y) != map_manager.start and (x, y) != map_manager.goal:
                empty_cells.append((x, y))
                
    random.shuffle(empty_cells)
    towers_to_place = min(num_towers, len(empty_cells))
    for i in range(towers_to_place):
        rx, ry = empty_cells[i]
        map_manager.add_tower(rx, ry, random.choice(types))
            
    if update_ui_callback: 
        update_ui_callback()

    T = 100.0
    Tmin = 10.0
    
    # Tính alpha động để đạt Tmin sau đúng số bước steps chỉ định
    if steps > 0:
        alpha = (Tmin / T) ** (1.0 / steps)
    else:
        alpha = 0.92

    current_energy = get_map_energy(map_manager)

    while T > Tmin:
        backup_towers = dict(map_manager.towers)
        
        # Di chuyển tháp ngẫu nhiên
        get_random_neighbor_layout(map_manager, num_towers)
        next_energy = get_map_energy(map_manager)
        
        delta = next_energy - current_energy
        
        # Nếu cấu hình mới tốt hơn (đường đi của quái dài ra)
        if delta < 0:
            current_energy = next_energy
            if log_callback:
                log_callback(f"🌡️ T={T:.1f} | Chấp nhận cấu hình tốt hơn. Đường đi: {-current_energy:.0f} ô.")
        # Nếu cấu hình mới tệ hơn, tính xác suất Boltzmann để quyết định
        else:
            p = math.exp(-delta / T)
            if random.random() < p:
                current_energy = next_energy
                if log_callback:
                    log_callback(f"🎲 T={T:.1f} | Chấp nhận cấu hình tệ hơn với p={p:.2f}. Đường đi: {-current_energy:.0f} ô.")
            else:
                map_manager.towers = backup_towers  # Khôi phục cấu hình tháp cũ nếu từ chối
                if log_callback:
                    log_callback(f"❌ T={T:.1f} | Từ chối cấu hình mới.")
                    
        T = max(Tmin, T * alpha)
        if update_ui_callback: 
            update_ui_callback()
            time.sleep(0.05)  # Tránh làm đơ giao diện bằng cách nhường quyền cho GUI thread