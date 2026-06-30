import time
import path_step_monitor

def solve(start, goal, map_manager, delay=0.0):
    """
    Giải bài toán tìm đường đi bằng giải thuật Quay lui CSP (Backtracking Constraint Satisfaction Problem).
    - Biến (Variables): Các bước đi tiếp theo trong chuỗi đường đi từ Start -> Goal.
    - Miền giá trị (Domain): 4 ô lân cận xung quanh vị trí hiện tại (Lên, Xuống, Trái, Phải).
    - Ràng buộc (Constraints): Ô kế tiếp phải nằm trong lưới, không phải vật cản (tháp), 
      chưa nằm trong đường đi hiện tại (để né lặp vòng tròn), và chưa bị đánh dấu thất bại trong lượt này.
    - Phép gán (Assignment): Chuỗi các ô tọa độ hợp lệ nối từ điểm xuất phát đến vị trí hiện tại.
    """
    path_step_monitor.log_step(f"Khởi chạy Backtracking CSP (Mô hình Bài toán Thỏa mãn Ràng buộc) từ {start}")
    
    step_count = 0
    max_steps = 5000 # Giới hạn an toàn tránh lặp đệ quy quá sâu gây treo hệ thống
    visited_nodes = set()
    
    def is_complete(assignment):
        # Điều kiện hoàn chỉnh: Phép gán chứa ít nhất 1 phần tử và phần tử cuối cùng chính là đích (goal)
        return len(assignment) > 0 and assignment[-1] == goal

    def is_consistent(value, assignment):
        """Kiểm tra xem giá trị ô tiếp theo 'value' đề xuất có thỏa mãn tất cả ràng buộc không."""
        x, y = value
        # Ràng buộc 1: Tọa độ nằm trong bản đồ hợp lệ
        if not map_manager.is_valid_coord(x, y):
            return False
        # Ràng buộc 2: Tọa độ không chứa tháp phòng thủ (obstacle)
        if map_manager.is_obstacle(x, y):
            return False
        # Ràng buộc 3: Tọa độ chưa xuất hiện trong chuỗi đường đi hiện tại (tránh lặp vô hạn)
        if value in assignment:
            return False
        # Ràng buộc 4: Tọa độ chưa bị đánh dấu thất bại (visited_nodes) khi đi từ nhánh này
        if value in visited_nodes:
            return False
        return True

    def get_domain_values(current_node):
        # Miền giá trị của biến tiếp theo là các ô lân cận xung quanh ô hiện tại
        return map_manager.get_neighbors(current_node[0], current_node[1])

    def recursive_backtracking(assignment):
        nonlocal step_count
        step_count += 1
        if step_count > max_steps:
            return None

        # 1. Nếu phép gán đã hoàn chỉnh (đến đích thành công), trả về kết quả
        if is_complete(assignment):
            curr = assignment[-1]
            path_step_monitor.log_step(f"🎉 Đã tìm thấy Solution tại đích {curr}!")
            return assignment

        # 2. Chọn biến tiếp theo (là ô đi tiếp theo từ vị trí cuối cùng của phép gán hiện tại)
        current_node = assignment[-1]
        visited_nodes.add(current_node)
        path_step_monitor.log_node_state(current_node[0], current_node[1], "open")
        
        if delay > 0:
            time.sleep(delay)

        # 3. Duyệt qua từng giá trị hàng xóm trong Miền giá trị
        domain_values = get_domain_values(current_node)
        
        for value in domain_values:
            # 4. Kiểm tra xem hướng đi này có thỏa mãn các ràng buộc cứng không
            if is_consistent(value, assignment):
                # Gán giá trị mới cho đường đi
                assignment.append(value)
                path_step_monitor.log_step(f"Gán giá trị hợp lệ: {value}")
                
                # Gọi đệ quy đi tiếp từ ô mới gán
                result = recursive_backtracking(assignment)
                if result is not None:
                    return result
                
                # NẾU THẤT BẠI: Tiến hành quay lui (Backtrack) - tháo bỏ phép gán
                assignment.pop()
                path_step_monitor.log_node_state(value[0], value[1], "reset")
                path_step_monitor.log_step(f"↩️ Quay lui (Backtrack) từ: {value}")
                if delay > 0:
                    time.sleep(delay)
                    
        return None

    # Bắt đầu thuật toán đệ quy quay lui với phép gán ban đầu chứa ô xuất phát [start]
    initial_assignment = [start]
    solution = recursive_backtracking(initial_assignment)
    
    if solution:
        # Đánh dấu đường đi hoàn chỉnh màu xanh lá cây trên GUI
        for px, py in solution:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return solution
        
    path_step_monitor.log_step("Không tìm thấy đường đi thỏa mãn ràng buộc!")
    return None


def solve_all_paths(start, goal, map_manager, max_steps=1000000, max_paths=200):
    """
    Thu thập TẤT CẢ các đường đi khả thi từ Start đến Goal bằng DFS quay lui.
    Dùng để hỗ trợ các thuật toán so sánh nhiều đường đi (Expectimax) trên GUI.
    """
    all_paths = []
    step_count = 0
    
    def dfs(assignment):
        nonlocal step_count
        # Dừng sớm nếu thu thập đủ số lượng đường đi hoặc vượt giới hạn bước duyệt an toàn
        if len(all_paths) >= max_paths or step_count > max_steps:
            return
            
        step_count += 1
        curr = assignment[-1]
        
        if curr == goal:
            all_paths.append(list(assignment))
            return
            
        neighbors = map_manager.get_neighbors(curr[0], curr[1])
        for nxt in neighbors:
            if nxt not in assignment:
                assignment.append(nxt)
                dfs(assignment)
                assignment.pop() # Quay lui sau khi xét xong nhánh con
                if len(all_paths) >= max_paths or step_count > max_steps:
                    break

    dfs([start])
    if step_count > max_steps and len(all_paths) == 0:
        path_step_monitor.log_step("⚠️ Quá trình quét dừng lại sớm vì vượt quá giới hạn số bước an toàn.")
    return all_paths
