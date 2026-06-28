import time
import path_step_monitor

def solve(start, goal, map_manager, delay=0.0):
    """
    Giải bài toán tìm đường bằng Thuật toán Quay lùi CSP (Constraint Satisfaction Problem).
    Dựa trên lý thuyết CSP:
    - Biến (Variables): Các ô tọa độ tiếp theo trên đường đi.
    - Miền giá trị (Domain): Tập hợp các ô lân cận 4 hướng (Trái, Phải, Trên, Dưới).
    - Ràng buộc (Constraints): Ô không phải vật cản, nằm trong lưới, chưa nằm trong assignment (né vòng lặp), và chưa nằm trong visited_nodes.
    - Phép gán (Assignment): Đường đi hiện tại từ start đến vị trí hiện tại.
    """
    path_step_monitor.log_step(f"Khởi chạy Backtracking CSP (Mô hình Bài toán Thỏa mãn Ràng buộc) từ {start}")
    
    step_count = 0
    max_steps = 5000
    visited_nodes = set()
    
    def is_complete(assignment):
        """Kiểm tra phép gán đã hoàn thành chưa (đã tới đích)."""
        return len(assignment) > 0 and assignment[-1] == goal

    def is_consistent(value, assignment):
        """Kiểm tra giá trị (ô tiếp theo) có thỏa mãn các ràng buộc không."""
        x, y = value
        # Ràng buộc 1: Phải là tọa độ hợp lệ trên bản đồ
        if not map_manager.is_valid_coord(x, y):
            return False
        # Ràng buộc 2: Không được là vật cản (trụ phòng thủ)
        if map_manager.is_obstacle(x, y):
            return False
        # Ràng buộc 3: Chưa được gán trong assignment hiện tại (tránh lặp vô tận)
        if value in assignment:
            return False
        # Ràng buộc 4: Chưa nằm trong visited_nodes (tránh khám phá lại ô đã duyệt)
        if value in visited_nodes:
            return False
        return True

    def get_domain_values(current_node):
        """Lấy miền giá trị (các ô lân cận) cho biến hiện tại."""
        return map_manager.get_neighbors(current_node[0], current_node[1])

    def recursive_backtracking(assignment):
        nonlocal step_count
        step_count += 1
        if step_count > max_steps:
            return None

        # 1. Kiểm tra nếu phép gán đã hoàn chỉnh (Solution is a complete + consistent assignment)
        if is_complete(assignment):
            curr = assignment[-1]
            path_step_monitor.log_step(f"🎉 Đã tìm thấy Solution tại đích {curr}!")
            return assignment

        # 2. Chọn biến chưa gán (ở đây là vị trí mở rộng tiếp theo từ cuối assignment)
        current_node = assignment[-1]
        visited_nodes.add(current_node)
        path_step_monitor.log_node_state(current_node[0], current_node[1], "open")
        
        if delay > 0:
            time.sleep(delay)

        # 3. Thử từng giá trị trong Miền giá trị cho biến đã được chọn
        domain_values = get_domain_values(current_node)
        
        for value in domain_values:
            # 4. Kiểm tra ràng buộc
            if is_consistent(value, assignment):
                # Nếu hợp lệ thì gán giá trị cho biến + gọi đệ quy
                assignment.append(value)
                path_step_monitor.log_step(f"Gán giá trị hợp lệ: {value}")
                
                result = recursive_backtracking(assignment)
                if result is not None:
                    return result
                
                # Nếu không thành công thì tháo bỏ phép gán (Backtrack)
                assignment.pop()
                path_step_monitor.log_node_state(value[0], value[1], "reset")
                path_step_monitor.log_step(f"↩️ Quay lui (Backtrack) từ: {value}")
                if delay > 0:
                    time.sleep(delay)
                    
        return None

    # Bắt đầu với 1 assignment rỗng (chứa vị trí xuất phát)
    initial_assignment = [start]
    solution = recursive_backtracking(initial_assignment)
    
    if solution:
        for px, py in solution:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return solution
        
    path_step_monitor.log_step("Không tìm thấy đường đi thỏa mãn ràng buộc!")
    return None


def solve_all_paths(start, goal, map_manager, max_steps=1000000, max_paths=200):
    """
    Quét và thu thập tất cả các phép gán (Solution) thỏa mãn ràng buộc.
    """
    all_paths = []
    step_count = 0
    
    def dfs(assignment):
        nonlocal step_count
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
                assignment.pop()
                if len(all_paths) >= max_paths or step_count > max_steps:
                    break

    dfs([start])
    if step_count > max_steps and len(all_paths) == 0:
        path_step_monitor.log_step("⚠️ Quá trình quét dừng lại sớm vì vượt quá giới hạn số bước an toàn.")
    return all_paths

