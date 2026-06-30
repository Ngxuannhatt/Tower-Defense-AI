import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    """
    Giải thuật DFS trong môi trường quan sát một phần (Belief State DFS).
    - Phù hợp khi tác nhân (agent) không thể biết chính xác vị trí hiện tại của mình trên bản đồ (do sương mù, tầm nhìn hạn chế).
    - Giải pháp: Biểu diễn vị trí bằng Trạng thái niềm tin (Belief State) - tập hợp tất cả các tọa độ 
      khả thi mà tác nhân có thể đang đứng (sử dụng cấu trúc `frozenset` để băm được trong Python).
    - Mục tiêu: Tìm kiếm một chuỗi các hành động di chuyển cố định (U, D, L, R) sao cho DÙ tác nhân có đứng ở ô nào
      trong trạng thái niềm tin đi chăng nữa, sau khi thực hiện chuỗi hành động này, nó chắc chắn hội tụ về Đích (Goal).
    """
    path_step_monitor.log_step(f"Khởi chạy DFS Partially Observable (Belief State DFS) từ {start} đến {goal}")
    
    # Trạng thái niềm tin ban đầu: Chỉ chứa duy nhất ô xuất phát (do ta biết rõ điểm xuất phát)
    initial_belief = frozenset([start])
    
    # Ngăn xếp DFS lưu các phần tử: (trạng thái_niềm_tin, danh_sách_hành_động_đã_thực_hiện)
    frontier = [(initial_belief, [])]
    
    # Tập hợp lưu các trạng thái niềm tin đã duyệt qua để tránh lặp vô hạn
    visited = {initial_belief}
    
    # Các hành động di chuyển hợp lệ tương ứng với tọa độ dịch chuyển
    actions = {
        'U': (0, -1), # Up (Lên)
        'D': (0, 1),  # Down (Xuống)
        'L': (-1, 0), # Left (Trái)
        'R': (1, 0)  # Right (Phải)
    }
    
    max_states = 5000
    state_count = 0
    
    while frontier and state_count < max_states:
        state_count += 1
        curr_belief, path_actions = frontier.pop() # Lấy trạng thái niềm tin ra khỏi ngăn xếp
        
        path_step_monitor.log_step(f"Mở trạng thái niềm tin: {list(curr_belief)}")
        for px, py in curr_belief:
            path_step_monitor.log_node_state(px, py, "closed")
            
        if delay > 0:
            time.sleep(delay)
            
        # Điều kiện dừng: Khi trạng thái niềm tin co cụm lại chỉ còn chứa duy nhất ô Đích (Goal)
        # Nghĩa là quái vật chắc chắn đã về đích, không còn khả năng đứng ở ô nào khác.
        if curr_belief == frozenset([goal]):
            path_step_monitor.log_step(f"🎉 Đã tìm thấy chuỗi hành động đưa mọi khả năng về đích: {path_actions}")
            
            # Truy vết ngược lại đường đi vật lý từ điểm xuất phát theo chuỗi hành động tìm được
            path = [start]
            curr = start
            for act in path_actions:
                dx, dy = actions[act]
                nx, ny = curr[0] + dx, curr[1] + dy
                if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
                    curr = (nx, ny)
                path.append(curr)
                
            # Tô vẽ đường đi vật lý này lên giao diện GUI
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        # Thử áp dụng từng hành động (U, D, L, R) lên trạng thái niềm tin hiện tại
        for act, (dx, dy) in actions.items():
            new_coords = []
            for px, py in curr_belief:
                if (px, py) == goal:
                    # Ràng buộc đứng yên: Nếu một khả năng đã chạm đích, nó sẽ đứng yên tại đích
                    new_coords.append(goal)
                else:
                    nx, ny = px + dx, py + dy
                    # Nếu hành động đưa tới ô hợp lệ, cập nhật tọa độ khả thi mới
                    if grid.is_valid_coord(nx, ny) and not grid.is_obstacle(nx, ny):
                        new_coords.append((nx, ny))
                    # Nếu đâm vào tường hoặc tháp chướng ngại vật, tác nhân đứng yên tại chỗ
                    else:
                        new_coords.append((px, py))
            next_belief = frozenset(new_coords) # Trạng thái niềm tin mới sau hành động
            
            # Nếu trạng thái niềm tin mới này chưa từng được khám phá
            if next_belief not in visited:
                visited.add(next_belief)
                # Đẩy trạng thái niềm tin mới và chuỗi hành động tích lũy vào ngăn xếp DFS
                frontier.append((next_belief, path_actions + [act]))
                
                path_step_monitor.log_step(f"  Hành động '{act}' -> Trạng thái niềm tin mới: {list(next_belief)}")
                for px, py in next_belief:
                    path_step_monitor.log_node_state(px, py, "open")
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
    path_step_monitor.log_step("Không tìm thấy chuỗi hành động khả thi trong môi trường quan sát một phần!")
    return None