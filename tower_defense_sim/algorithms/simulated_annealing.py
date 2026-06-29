import math
import random
import time
import path_step_monitor
from algorithms import astar

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    Tìm kiếm đường đi bằng Simulated Annealing chuẩn theo mã giả.
    Giữ nguyên cấu trúc để import vào hàm main của GUI.
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
        
        # Nếu đã đạt tới đích -> Trả về trạng thái hiện tại (Đúng theo mã giả)
        if current == goal:
            break
            
        path_step_monitor.log_node_state(x, y, "closed")
        if delay > 0:
            time.sleep(delay)
            
        # Lấy tất cả các ô hàng xóm hợp lệ trên lưới xung quanh ô hiện tại
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
                neighbors.append((nx, ny))
                
        if not neighbors:
            path_step_monitor.log_step(f"Bị kẹt tại {current} vì không có hàng xóm hợp lệ!")
            break
            
        # 1. Chọn NGẪU NHIÊN một ô hàng xóm (RandomNeighbor) theo đúng mã giả
        next_state = random.choice(neighbors)
        
        # 2. Tính Delta = h(next_state) - h(current_state)
        # Vì bài toán tìm đường là bài toán TÌM MIN (h càng nhỏ càng tốt)
        delta = h(next_state) - h(current)
        
        # 3. Nếu ô tiếp theo tốt hơn (delta < 0) -> Chấp nhận di chuyển
        if delta < 0:
            current = next_state
            path.append(current)
            path_step_monitor.log_step(f"🌡️ T={T:.1f} | Chấp nhận ô tốt hơn: {current} (h={h(current)})")
        # 4. Ngược lại nếu ô tiếp theo tệ hơn -> Xét xác suất Boltzmann
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
        
        # 5. QUAN TRỌNG: Hạ nhiệt độ sau MỖI bước thử (Bất kể chấp nhận hay từ chối)
        # Điều này đảm bảo vòng lặp while luôn kết thúc và không bị lặp vô hạn.
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
    """Tính toán năng lượng dựa trên độ dài đường đi ngắn nhất của A*."""
    path = astar.solve(map_manager.start, map_manager.goal, map_manager, delay=0.0)
    if path is None:
        return 999.0  # Phạt nặng cấu hình chặn đường đi
    return -len(path)


def get_random_neighbor_layout(map_manager, num_towers):
    """
    Sửa lỗi vòng lặp vô hạn khi random vị trí tháp trên bản đồ chật hẹp.
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
    Tối ưu hóa vị trí các tháp thủ thành bằng Simulated Annealing.
    """
    map_manager.reset()
    types = ["Basic", "Ice", "Fire"]
    
    # Thu thập toàn bộ ô trống để rải tháp ban đầu an toàn, tránh lặp vô hạn
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
        
        get_random_neighbor_layout(map_manager, num_towers)
        next_energy = get_map_energy(map_manager)
        
        delta = next_energy - current_energy
        
        if delta < 0:
            current_energy = next_energy
            if log_callback:
                log_callback(f"🌡️ T={T:.1f} | Chấp nhận cấu hình tốt hơn. Đường đi: {-current_energy:.0f} ô.")
        else:
            p = math.exp(-delta / T)
            if random.random() < p:
                current_energy = next_energy
                if log_callback:
                    log_callback(f"🎲 T={T:.1f} | Chấp nhận cấu hình tệ hơn với p={p:.2f}. Đường đi: {-current_energy:.0f} ô.")
            else:
                map_manager.towers = backup_towers  # Khôi phục nếu từ chối
                if log_callback:
                    log_callback(f"❌ T={T:.1f} | Từ chối cấu hình mới.")
                    
        T = max(Tmin, T * alpha)
        if update_ui_callback: 
            update_ui_callback()
            time.sleep(0.05)  # Tránh làm đơ giao diện bằng cách nhường quyền cho GUI thread