from collections import deque
import time
import path_step_monitor

def belief_state_search(possible_starts: list, goal: tuple, grid) -> list:
    """
    Tìm kiếm Trạng thái niềm tin sử dụng thuật toán duyệt theo chiều rộng (BFS).
    - Duyệt theo chiều rộng giúp đảm bảo tìm thấy chuỗi hành động di chuyển (U, D, L, R) 
      có độ dài ngắn nhất để đưa mọi khả năng di chuyển về đích.
    - possible_starts: Danh sách các ô xuất phát khả thi (tập trạng thái niềm tin ban đầu).
    - goal: Ô đích vật lý cần quy tụ về.
    - grid: Đối tượng quản lý bản đồ.
    """
    initial_state = frozenset(possible_starts)
    # Hàng đợi FIFO lưu trữ: (trạng thái_niềm_tin, danh_sách_hành_động)
    queue = deque([(initial_state, [])])
    visited = {initial_state}
    
    # Định nghĩa dịch chuyển tương ứng với 4 hướng hành động
    actions = {
        'U': (0, -1),
        'D': (0, 1),
        'L': (-1, 0),
        'R': (1, 0)
    }
    
    max_states = 10000
    state_count = 0
    
    while queue and state_count < max_states:
        state_count += 1
        current_state, path_actions = queue.popleft() # Lấy phần tử đầu hàng đợi (FIFO)
        
        # Điều kiện thắng: Trạng thái niềm tin co cụm lại thành duy nhất một ô Đích.
        if current_state == frozenset([goal]):
            return path_actions
            
        # Thử áp dụng các hành động di chuyển
        for act, (dx, dy) in actions.items():
            new_coords = []
            for px, py in current_state:
                if (px, py) == goal:
                    # Nếu một hạt giả định đã chạm đích, nó đứng yên tại đích
                    new_coords.append(goal)
                else:
                    nx, ny = px + dx, py + dy
                    if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
                        new_coords.append((nx, ny))
                    else:
                        # Đứng yên tại chỗ nếu va vào tường hoặc tháp
                        new_coords.append((px, py))
                        
            next_state = frozenset(new_coords)
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path_actions + [act]))
                
    return []

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    Hàm bao ngoài (wrapper) tương thích với hệ thống vẽ đường đi của GUI.
    - Chuyển đổi kết quả chuỗi hành động ký tự (như ['U', 'R', 'R']) thành tọa độ vật lý
      để trực quan hóa quá trình quái di chuyển trên lưới GUI.
    """
    path_step_monitor.log_step(f"Khởi chạy Belief State Search từ {start} đến {goal}")
    
    # Theo mặc định, giả định điểm xuất phát ban đầu là duy nhất (start)
    possible_starts = [start]
    
    # Tìm kiếm chuỗi hành động tối ưu bằng BFS
    actions_list = belief_state_search(possible_starts, goal, grid)
    
    if not actions_list:
        path_step_monitor.log_step("Không tìm thấy chuỗi hành động niềm tin mù!")
        return None
        
    path_step_monitor.log_step(f"Belief State Search tìm thấy chuỗi hành động: {actions_list}")
    
    # Tái hiện tọa độ vật lý từ điểm xuất phát theo chuỗi hành động để hiển thị trên GUI
    path = [start]
    curr = start
    for act in actions_list:
        dx, dy = 0, 0
        if act == 'U': dy = -1
        elif act == 'D': dy = 1
        elif act == 'L': dx = -1
        elif act == 'R': dx = 1
        
        nx, ny = curr[0] + dx, curr[1] + dy
        if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
            curr = (nx, ny)
        # Vẫn ghi nhận tọa độ ngay cả khi đứng yên để bước mô phỏng vẽ chính xác
        path.append(curr)
        
        path_step_monitor.log_node_state(curr[0], curr[1], "closed")
        if delay > 0:
            time.sleep(delay * 0.1)
            
    # Đánh dấu đường đi tối ưu màu path
    for px, py in path:
        if (px, py) != start and (px, py) != goal:
            path_step_monitor.log_node_state(px, py, "path")
            
    return path
