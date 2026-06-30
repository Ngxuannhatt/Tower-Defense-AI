import time
import path_step_monitor

def steepest_ascent_hill_climbing(start: tuple, goal: tuple, grid) -> list:
    """
    Hàm leo đồi dốc đứng (Steepest Ascent Hill Climbing) tiêu chuẩn.
    Sử dụng thêm bộ nhớ (visited_cells) làm kỹ thuật tránh rơi vào vòng lặp vô hạn ở cực đại cục bộ.
    """
    visited_cells = {start}
    path = [start]
    current = start
    
    max_steps = 1000
    steps = 0
    
    while current != goal and steps < max_steps:
        steps += 1
        x, y = current
        
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny) and (nx, ny) not in visited_cells:
                neighbors.append((nx, ny))
                
        if not neighbors:
            break
            
        # Tìm ô lân cận có khoảng cách Manhattan tới đích ngắn nhất
        best_neighbor = min(neighbors, key=lambda n: abs(n[0] - goal[0]) + abs(n[1] - goal[1]))
        
        current = best_neighbor
        visited_cells.add(current)
        path.append(current)
        
    if path[-1] == goal:
        return path
    return None

def solve(start: tuple, goal: tuple, grid, delay=0.0) -> list:
    """
    Giải thuật Tìm kiếm Leo đồi dốc đứng (Steepest Ascent Hill Climbing).
    - Tại mỗi bước, thuật toán đánh giá tất cả các ô hàng xóm lân cận và luôn di chuyển 
      đến ô cải thiện giá trị tốt nhất (khoảng cách Manhattan tới đích nhỏ nhất).
    - Hạn chế: Dễ bị kẹt tại "Cực đại cục bộ" (Local Maxima - nơi tất cả các hàng xóm đều tệ hơn ô hiện tại, 
      nhưng vẫn chưa phải là đích).
    - Giải pháp tích hợp: Sử dụng danh sách `visited_cells` để không quay lại ô cũ, cho phép đi tiếp 
      sang ô lân cận tốt nhất tiếp theo ngay cả khi nó không tốt hơn ô hiện tại (leo qua sườn đồi).
    """
    path_step_monitor.log_step(f"Khởi chạy Steepest Ascent Hill Climbing từ {start} đến {goal}")
    
    visited_cells = {start}
    path = [start]
    current = start
    
    max_steps = 1000
    steps = 0
    
    while current != goal and steps < max_steps:
        steps += 1
        x, y = current
        
        path_step_monitor.log_node_state(x, y, "closed")
        if delay > 0:
            time.sleep(delay)
            
        # Lấy danh sách hàng xóm hợp lệ 4 hướng xung quanh ô hiện tại
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny) and (nx, ny) not in visited_cells:
                neighbors.append((nx, ny))
                
        # Nếu không còn ô lân cận trống nào chưa đi qua, kết thúc tìm kiếm
        if not neighbors:
            path_step_monitor.log_step(f"Cực đại cục bộ không còn lối đi lân cận trống tại {current}!")
            break
            
        # Sắp xếp các ô lân cận theo thứ tự khoảng cách Manhattan tới đích tăng dần
        neighbors.sort(key=lambda n: abs(n[0] - goal[0]) + abs(n[1] - goal[1]))
        best_neighbor = neighbors[0] # Chọn ô lân cận tốt nhất
        
        curr_dist = abs(current[0] - goal[0]) + abs(current[1] - goal[1])
        best_dist = abs(best_neighbor[0] - goal[0]) + abs(best_neighbor[1] - goal[1])
        
        # Nếu khoảng cách của ô lân cận tốt nhất vẫn lớn hơn hoặc bằng ô hiện tại,
        # nghĩa là chúng ta đang ở cực đại cục bộ (hoặc vùng phẳng phẳng).
        if best_dist >= curr_dist:
            path_step_monitor.log_step(f"Rơi vào cực đại cục bộ tại {current} (d={curr_dist}). Đi tiếp ô lân cận tốt nhất tiếp theo {best_neighbor} (d={best_dist}).")
        else:
            path_step_monitor.log_step(f"Đi tới ô tốt hơn: {best_neighbor} (d={best_dist} < {curr_dist})")
            
        current = best_neighbor
        visited_cells.add(current)
        path.append(current)
        
        # Cập nhật trạng thái hiển thị trên giao diện
        path_step_monitor.log_node_state(current[0], current[1], "open")
        
    # Kiểm tra xem có thực sự dừng ở đích hay không
    if path[-1] == goal:
        path_step_monitor.log_step(f"Hill Climbing đã tìm thấy đích! Độ dài: {len(path)}")
        for px, py in path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return path
        
    path_step_monitor.log_step("Không tìm thấy đường đi tới đích!")
    return None
