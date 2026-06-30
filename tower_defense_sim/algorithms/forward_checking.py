import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    """
    Giải thuật Quay lui kết hợp kiểm tra trước (Backtracking with Forward Checking).
    - Là một kỹ thuật tối ưu hóa trong bài toán thỏa mãn ràng buộc (CSP).
    - Ý tưởng: Tại mỗi bước gán giá trị (đi vào ô neighbor), ta "nhìn trước" (Look Ahead) bằng cách 
      chạy thử một thuật toán duyệt nhanh (BFS) để kiểm tra xem từ ô neighbor đó còn tồn tại đường đi 
      về đích mà không đè lên các ô đã gán (assignment/path hiện tại) hay không.
    - Cắt tỉa (Pruning): Nếu không còn đường đi về đích từ ô neighbor đó (Forward Checking thất bại), 
      ta loại bỏ ngay ô neighbor đó khỏi miền giá trị, không gọi đệ quy sâu xuống nữa. 
      Điều này giúp tiết kiệm lượng lớn tài nguyên và thời gian duyệt nhánh cụt.
    """
    path_step_monitor.log_step(f"Khởi chạy Backtracking với Forward Checking từ {start}")
    
    assignment = []
    step_count = 0
    max_steps = 2000
    
    def is_connected_to_goal(node, visited_set):
        """
        Hàm nhìn trước (Forward Checking): Chạy BFS nhanh từ ô 'node' ứng viên tới 'goal'.
        Chỉ duyệt qua các ô trống chưa nằm trong visited_set (chuỗi đường đi hiện tại).
        """
        if node == goal:
            return True
        queue = [node]
        seen = {node}
        while queue:
            curr = queue.pop(0)
            if curr == goal:
                return True
            neighbors = grid.get_neighbors(curr[0], curr[1])
            for nxt in neighbors:
                if nxt not in visited_set and nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return False

    def backtrack(curr):
        nonlocal step_count
        step_count += 1
        if step_count > max_steps:
            return False
            
        if curr == goal:
            assignment.append(curr)
            path_step_monitor.log_step(f"🎉 Đã tìm thấy đích tại {curr}!")
            return True
            
        assignment.append(curr)
        path_step_monitor.log_node_state(curr[0], curr[1], "open")
        path_step_monitor.log_step(f"Gán giá trị: {curr}")
        if delay > 0:
            time.sleep(delay)
            
        neighbors = grid.get_neighbors(curr[0], curr[1])
        # Sắp xếp các ô lân cận theo thứ tự khoảng cách Manhattan tới đích tăng dần (Heuristic ưu tiên hướng tốt)
        neighbors.sort(key=lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1]))
        
        visited_set = set(assignment)
        
        for neighbor in neighbors:
            if neighbor not in visited_set:
                # --- BƯỚC KIỂM TRA TRƯỚC (FORWARD CHECKING) ---
                path_step_monitor.log_step(f"  🔍 Forward Checking: Kiểm tra xem từ {neighbor} có tới được {goal} không...")
                
                # Chạy BFS kiểm tra liên thông tới đích từ neighbor này
                if is_connected_to_goal(neighbor, visited_set):
                    path_step_monitor.log_step(f"  ✅ FC Thành công: Từ {neighbor} vẫn còn đường đi tới đích.")
                    # Nếu FC thành công, gọi đệ quy đi tiếp sang ô lân cận này
                    if backtrack(neighbor):
                        return True
                else:
                    # Nếu FC thất bại (bị tháp chặn ngõ cụt), tiến hành cắt tỉa ngay lập tức
                    path_step_monitor.log_step(f"  ❌ FC Thất bại: Cắt tỉa (Prune) {neighbor} vì không thể đi tới đích từ đây.")
                    path_step_monitor.log_node_state(neighbor[0], neighbor[1], "closed")
                    if delay > 0:
                        time.sleep(delay * 0.5)
                    path_step_monitor.log_node_state(neighbor[0], neighbor[1], "reset")
                    
        # Quay lui nếu tất cả các lựa chọn hàng xóm đều thất bại
        assignment.pop()
        path_step_monitor.log_node_state(curr[0], curr[1], "reset")
        path_step_monitor.log_step(f"↩️ Quay lui từ: {curr}")
        if delay > 0:
            time.sleep(delay)
        return False

    if backtrack(start):
        # Đánh dấu đường đi tối ưu cuối cùng màu path
        for px, py in assignment:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return assignment
        
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None