import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    """
    Giải thuật Tìm kiếm Chùm tia Cục bộ (Local Beam Search).
    - Là một biến thể của tìm kiếm local search nhưng lưu giữ đồng thời k trạng thái tốt nhất
      (thay vì chỉ lưu 1 trạng thái như Leo đồi).
    - Ở mỗi bước lặp, tất cả các nút lân cận (successors) của cả k trạng thái sẽ được sinh ra.
    - Nếu có bất kỳ hạt nào chạm đích, giải thuật kết thúc và trả về đường đi.
    - Ngược lại, ta chỉ giữ lại k hạt có giá trị Heuristic tốt nhất (khoảng cách Manhattan ngắn nhất) 
      để đi tiếp vào vòng lặp sau.
    - Kỹ thuật nâng cao: Lọc bỏ các hạt có cùng tọa độ cuối (seen_ends) để giữ độ đa dạng cho chùm tia.
    """
    k = 4 # Kích thước chùm tia (beam size) - theo dõi 4 đường đi hứa hẹn nhất cùng lúc
    path_step_monitor.log_step(f"Khởi chạy Local Beam Search (k={k}) từ {start} đến {goal}")
    
    def h(pos):
        # Khoảng cách Manhattan từ tọa độ hiện tại tới đích
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
    # Chùm tia (beam) lưu trữ danh sách các bộ: (heuristic_value, path_list)
    beam = [(h(start), [start])]
    
    max_steps = 150
    for step in range(max_steps):
        path_step_monitor.log_step(f"--- Bước {step+1}: Kích thước chùm hạt hiện tại = {len(beam)} ---")
        
        # Bước 1: Kiểm tra xem có đường đi nào trong chùm tia đã chạm đích chưa
        for _, path in beam:
            if path[-1] == goal:
                path_step_monitor.log_step(f"🎉 Chùm hạt đã đạt tới đích: {path}")
                # Tô vẽ đường đi cuối cùng màu path trên GUI
                for px, py in path:
                    if (px, py) != start and (px, py) != goal:
                        path_step_monitor.log_node_state(px, py, "path")
                return path
                
        # Bước 2: Phát triển các hạt con (successors) cho tất cả các hạt hiện tại trong chùm tia
        successors = []
        for _, path in beam:
            curr = path[-1]
            path_step_monitor.log_node_state(curr[0], curr[1], "closed")
            
            # Lấy các ô hàng xóm lân cận
            neighbors = grid.get_neighbors(curr[0], curr[1])
            for neighbor in neighbors:
                # Tránh đi lùi vào chính đường đi của hạt đó (tránh chu trình cục bộ)
                if neighbor not in path:
                    new_path = path + [neighbor]
                    successors.append((h(neighbor), new_path))
                    path_step_monitor.log_node_state(neighbor[0], neighbor[1], "open")
                    
        # Nếu không sinh thêm được hạt con nào nữa, kết thúc
        if not successors:
            path_step_monitor.log_step("Không còn node lân cận nào để mở rộng!")
            break
            
        if delay > 0:
            time.sleep(delay)
            
        # Bước 3: Sắp xếp tất cả các hạt con theo Heuristic tăng dần (tốt nhất xếp trước)
        successors.sort(key=lambda item: item[0])
        
        # Bước 4: Lọc bỏ các hạt trùng lặp tọa độ đích cuối cùng (seen_ends)
        # Việc này cực kỳ quan trọng để ngăn chùm tia hội tụ về cùng một đường đi duy nhất từ sớm.
        seen_ends = set()
        unique_successors = []
        for heur, path in successors:
            end_node = path[-1]
            if end_node not in seen_ends:
                seen_ends.add(end_node)
                unique_successors.append((heur, path))
                
        # Giữ lại k hạt tốt nhất và độc nhất
        beam = unique_successors[:k]
        
        if not beam:
            path_step_monitor.log_step("Chùm hạt bị triệt tiêu hoàn toàn!")
            break
            
        # Ghi log các tọa độ đầu chùm tia được chọn tiếp theo
        beam_ends = [path[-1] for _, path in beam]
        path_step_monitor.log_step(f"Chọn {len(beam)} hạt tốt nhất tiếp theo: {beam_ends}")
        
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None