import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    """
    Giải thuật Tìm kiếm Sâu dần Lặp lại A* (IDA* - Iterative Deepening A*).
    - Kết hợp khả năng tiết kiệm bộ nhớ của DFS và hiệu quả heuristic của A*.
    - Thay vì lưu trữ toàn bộ cây tìm kiếm trong RAM như A*, IDA* sử dụng tìm kiếm sâu dần (DFS) 
      nhưng giới hạn độ sâu dựa trên tổng chi phí ước lượng f (f-limit hay threshold).
    - Nếu f(n) của nhánh vượt quá ngưỡng threshold, nhánh đó sẽ bị cắt tỉa (pruning).
    - Ngưỡng threshold ban đầu được đặt bằng h(start), sau mỗi lượt duyệt thất bại sẽ được cập nhật
      bằng giá trị f nhỏ nhất vượt quá ngưỡng cũ.
    """
    path_step_monitor.log_step(f"Khởi chạy IDA* từ {start} đến {goal}")
    
    def h(pos):
        # Khoảng cách Manhattan ước lượng tới đích
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
    def search(path, g, threshold, visited):
        """
        Hàm DFS đệ quy có giới hạn ngưỡng threshold để tìm kiếm đường đi.
        - path: Danh sách các nút nằm trên nhánh DFS đang xét.
        - g: Chi phí thực tế đi từ start đến nút hiện tại.
        - threshold: Giới hạn f-limit tối đa cho phép trong lượt lặp hiện tại.
        - visited: Ghi nhận chi phí g tốt nhất của các ô trong lượt lặp hiện tại để tránh chu trình.
        """
        curr = path[-1]
        f = g + h(curr)
        
        # Cập nhật trực quan hóa nút đang mở rộng trên GUI
        path_step_monitor.log_node_state(curr[0], curr[1], "closed")
        path_step_monitor.log_step(f"Xét node: {curr}, g={g}, h={h(curr)}, f={f} (Ngưỡng: {threshold})")
        if delay > 0:
            time.sleep(delay)
            
        # Cắt tỉa nếu tổng chi phí ước lượng f lớn hơn ngưỡng giới hạn cho phép
        if f > threshold:
            return f, None
            
        # Nếu đạt tới đích, trả về đường đi
        if curr == goal:
            return f, list(path)
            
        min_val = float('inf')
        neighbors = grid.get_neighbors(curr[0], curr[1])
        
        # Tối ưu hóa: Sắp xếp các ô lân cận theo thứ tự heuristic tăng dần (gần đích nhất xét trước)
        # Việc này giúp tìm thấy đích nhanh hơn và cắt tỉa hiệu quả hơn.
        neighbors.sort(key=lambda p: h(p))
        
        for neighbor in neighbors:
            if neighbor not in path:
                # Tránh chu trình: Nếu hàng xóm đã được ghé thăm trong nhánh khác của lượt lặp này
                # với chi phí g rẻ hơn hoặc bằng, ta bỏ qua không duyệt lại nữa.
                if neighbor in visited and g + 1.0 >= visited[neighbor]:
                    continue
                visited[neighbor] = g + 1.0
                
                path.append(neighbor)
                path_step_monitor.log_node_state(neighbor[0], neighbor[1], "open")
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
                # Gọi đệ quy đi sâu tiếp xuống nút con
                t, found_path = search(path, g + 1.0, threshold, visited)
                if found_path is not None:
                    return t, found_path
                
                # Cập nhật lại ngưỡng nhỏ nhất tiếp theo vượt quá threshold hiện tại
                if t < min_val:
                    min_val = t
                
                # Quay lui (backtracking): Rút nút ra khỏi đường đi và khôi phục trạng thái hiển thị
                path.pop()
                path_step_monitor.log_node_state(neighbor[0], neighbor[1], "reset")
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
        return min_val, None

    # Khởi tạo ngưỡng threshold ban đầu bằng khoảng cách Heuristic của nút xuất phát
    threshold = h(start)
    path = [start]
    path_step_monitor.log_node_state(start[0], start[1], "open")
    
    max_iterations = 200 # Giới hạn an toàn để tránh treo ứng dụng khi bản đồ quá lớn/phức tạp
    for iteration in range(max_iterations):
        path_step_monitor.log_step(f"--- Lượt lặp mới với ngưỡng f-limit = {threshold} ---")
        visited = {start: 0.0}
        
        # Chạy DFS từ nút xuất phát với ngưỡng hiện tại
        t, found_path = search(path, 0.0, threshold, visited)
        
        # Nếu tìm thấy đường đi hoàn chỉnh, trả về kết quả
        if found_path is not None:
            path_step_monitor.log_step(f"IDA* tìm thấy đường đi: {found_path}")
            for px, py in found_path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return found_path
            
        # Nếu ngưỡng tiếp theo là vô hạn, nghĩa là đã duyệt toàn bộ không gian nhưng không có đường đi
        if t == float('inf'):
            path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
            return None
            
        # Tăng ngưỡng threshold lên mức f nhỏ nhất vừa vượt quá ngưỡng cũ để chuẩn bị cho lượt lặp sau
        threshold = t
        
    path_step_monitor.log_step("Đạt giới hạn số lượt lặp tối đa của IDA*!")
    return None