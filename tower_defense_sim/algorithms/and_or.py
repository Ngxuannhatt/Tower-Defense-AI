import random
import time
import path_step_monitor

def solve(start, goal, map_manager, delay=0.0, return_all=False):
    """
    Giải thuật Tìm kiếm VÀ-HOẶC (AND-OR Graph Search).
    - Dùng để lập kế hoạch trong môi trường không xác định (non-deterministic).
    - Ở đây, môi trường không xác định do sự hiện diện của Tháp Băng (Ice Tower): 
      quái đi qua có thể bị làm chậm (slowed) hoặc đi bình thường (normal).
    - Nút HOẶC (OR Node): Quái vật tự chọn hướng di chuyển (Lên, Xuống, Trái, Phải). 
      Nó chỉ cần 1 trong các hướng đi dẫn tới đích.
    - Nút VÀ (AND Node): Môi trường quyết định trạng thái của quái vật (bị làm chậm hoặc không).
      Chiến lược cần phải bao quát TẤT CẢ các phản ứng có thể xảy ra của môi trường (tức là dù bị làm chậm
      hay đi bình thường thì vẫn phải có đường đi tiếp theo hợp lệ để về đích).
    """
    path_step_monitor.log_step(f"Khởi chạy AND_OR_GRAPH_SEARCH từ {start}")
    
    MAX_DEPTH = 80       # Giới hạn độ sâu đệ quy tối đa để tránh quái đi vòng quanh vô tận
    MAX_PATHS = 100      # Số lượng đường đi ứng viên tối đa cần thu thập nhanh
    MAX_STEPS = 50000    # Giới hạn số bước duyệt tối đa để tránh tràn bộ nhớ CPU
    
    def goal_test(state):
        return state == goal

    def get_actions(state):
        # Lấy các ô lân cận trống (Nút OR - các hướng quái chọn đi)
        return map_manager.get_neighbors(state[0], state[1])

    def get_results(state, action):
        """
        Nút AND: Phản ứng của môi trường khi đi vào ô 'action'.
        Nếu ô đó nằm trong tầm bắn của tháp Ice, có xác suất bị đóng băng ("slowed") hoặc bình thường ("normal").
        Chiến lược lập kế hoạch bắt buộc phải giải quyết được cả 2 tình huống này.
        """
        prob = map_manager.get_freeze_probability(action[0], action[1])
        if prob > 0:
            return [("slowed", action), ("normal", action)] # Môi trường phân nhánh AND
        else:
            return [("normal", action)] # Môi trường xác định bình thường

    strategy_map = {} # Bản đồ lưu chiến lược dự phòng: (vị trí, trạng thái_môi_trường) -> ô đi tiếp theo
    all_extracted_paths = []
    step_count = 0
    visited_visuals = set()
    
    def find_all_strategy_paths(current_node, current_path, depth):
        nonlocal step_count
        step_count += 1
        
        # Kiểm tra các giới hạn an toàn để thoát sớm
        if len(all_extracted_paths) >= MAX_PATHS or depth >= MAX_DEPTH or step_count > MAX_STEPS:
            return
            
        # Nếu đã đạt tới đích, ghi nhận đường đi hoàn chỉnh này vào tập kết quả
        if current_node == goal:
            full_p = current_path + [current_node]
            if full_p not in all_extracted_paths:
                all_extracted_paths.append(full_p)
            return

        actions = get_actions(current_node)
        # Tối ưu hóa: Ưu tiên duyệt các hành động có hướng đi gần đích trước (Greedy Heuristic)
        actions.sort(key=lambda a: abs(a[0] - goal[0]) + abs(a[1] - goal[1]))

        for action in actions:
            if action not in current_path:
                if delay > 0 and action not in visited_visuals:
                    visited_visuals.add(action)
                    path_step_monitor.log_node_state(action[0], action[1], "open")
                    time.sleep(delay)
                    
                # Nhận tất cả các kết quả phân nhánh của môi trường (Nút AND)
                result_states = get_results(current_node, action)
                for env_status, nxt in result_states:
                    key = (current_node[0], current_node[1], env_status)
                    if key not in strategy_map:
                        strategy_map[key] = []
                    if nxt not in strategy_map[key]:
                        strategy_map[key].append(nxt)
                
                # Gọi đệ quy để tiếp tục lập kế hoạch cho ô tiếp theo
                find_all_strategy_paths(action, current_path + [current_node], depth + 1)
                if len(all_extracted_paths) >= MAX_PATHS or step_count > MAX_STEPS:
                    break
 
    # Khởi chạy tìm kiếm chiến lược đệ quy từ start
    find_all_strategy_paths(start, [], 0)
    
    if all_extracted_paths:
        path_step_monitor.log_step(f"AND-OR Search: Tìm thấy chiến lược với {len(all_extracted_paths)} đường đi khả thi!")
        
        # Định dạng lại strategy_map để phục vụ việc tra cứu nhanh trong mô phỏng di chuyển quái
        sim_strategy = {}
        for k, v in strategy_map.items():
            if isinstance(v, list) and len(v) > 0:
                sim_strategy[k] = v[0]
            else:
                sim_strategy[k] = v
        map_manager.last_and_or_strategy = sim_strategy
        
        if return_all:
            return all_extracted_paths

        # Chọn ngẫu nhiên một đường đi mẫu trong số các đường đi khả thi để trực quan hóa
        selected_path = random.choice(all_extracted_paths)
        path_step_monitor.log_step(f"🎲 AND-OR Search đã ngẫu nhiên chọn 1 đường đi trong số {len(all_extracted_paths)} đường khả thi!")
        for px, py in selected_path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
                
        return selected_path

    path_step_monitor.log_step("AND-OR Search: Không tìm thấy chiến lược khả thi trong giới hạn an toàn!")
    return None if not return_all else []
