import heapq
import time
import path_step_monitor

def solve(start, goal, map_manager, delay=0.0):
    """
    Giải thuật Tìm kiếm Expectimax kết hợp Hàng đợi ưu tiên.
    - Khác với Minimax giả định đối thủ luôn đi nước đi tối ưu nhất để hại ta, 
      Expectimax mô hình hóa các tình huống mang tính ngẫu nhiên của môi trường thông qua Nút cơ hội (Chance Nodes).
    - Ở đây, tháp Băng (Ice Tower) gây ra hiệu ứng đóng băng ngẫu nhiên (chậm chân). 
      Khi bị làm chậm, quái vật sẽ ở lâu hơn trong tầm bắn và nhận nhiều sát thương hơn.
    - Mục tiêu: Tìm kiếm đường đi có tổng sát thương kỳ vọng (Expected Damage) nhỏ nhất
      (tương đương lượng máu HP sống sót về đích là lớn nhất).
    """
    path_step_monitor.log_step(f"Khởi chạy EXPECTIMAX (Tối ưu hóa né sát thương - Máu tốn ít nhất) từ {start} đến {goal}")
    
    # Hàng đợi ưu tiên lưu các phần tử: (priority_score, accumulated_expected_damage, distance_to_goal, current_pos, path)
    # Sắp xếp ưu tiên theo tổng sát thương tích lũy để luôn duyệt đường đi an toàn nhất trước.
    start_h = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    pq = [(start_h * 0.05, 0.0, start_h, start, [start])]
    
    # Từ điển theo dõi lượng sát thương tối thiểu tích lũy để tới được từng ô
    min_damage_to_node = {start: 0.0}
    visited_nodes = set()
    
    while pq:
        # Lấy nút có điểm ưu tiên thấp nhất (tốt nhất) ra khỏi Heap
        p_score, acc_damage, h_dist, curr, path = heapq.heappop(pq)
        
        if curr in visited_nodes:
            continue
        visited_nodes.add(curr)
        
        # Trực quan hóa nút duyệt trên GUI
        if curr != start and curr != goal:
            path_step_monitor.log_node_state(curr[0], curr[1], "closed")
            if delay > 0:
                time.sleep(delay)
                
        # Khi chạm tới đích, tính toán và in kết quả lượng máu sống sót kỳ vọng
        if curr == goal:
            remaining_hp = max(0.0, 100.0 - acc_damage)
            path_step_monitor.log_step(f"Expectimax: Tìm thấy đường đi tốn ít máu nhất! Dài {len(path)} ô | Sát thương kỳ vọng: {acc_damage:.1f} | HP còn lại: {remaining_hp:.1f}/100")
            
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        x, y = curr
        neighbors = map_manager.get_neighbors(x, y)
        
        for nxt in neighbors:
            if nxt in visited_nodes:
                continue
                
            nx, ny = nxt
            # Lấy sát thương cơ bản và tỷ lệ đóng băng của tháp tại ô hàng xóm này
            base_dmg = map_manager.get_expected_damage(nx, ny)
            freeze_prob = map_manager.get_freeze_probability(nx, ny)
            
            # --- ĐÁNH GIÁ NÚT CƠ HỘI (CHANCE NODE EVALUATION) ---
            # Công thức sát thương kỳ vọng tại một ô:
            # Sát thương kỳ vọng = Sát thương cơ bản * (1.0 + Tỷ lệ đóng băng)
            # Tỷ lệ đóng băng càng cao làm quái đi chậm, tăng số lượt bị bắn lên gấp đôi.
            expected_step_dmg = base_dmg * (1.0 + freeze_prob)
            
            # Sát thương tích lũy mới (cộng thêm một chi phí bước đi rất nhỏ 0.001 để ưu tiên đường ngắn hơn khi bằng sát thương)
            new_acc_damage = acc_damage + expected_step_dmg + 0.001
            
            # Cập nhật nếu tìm thấy đường đi tới ô 'nxt' có tổng sát thương kỳ vọng nhỏ hơn
            if nxt not in min_damage_to_node or new_acc_damage < min_damage_to_node[nxt]:
                min_damage_to_node[nxt] = new_acc_damage
                nxt_h = abs(nx - goal[0]) + abs(ny - goal[1])
                
                # Điểm số ưu tiên kết hợp tối thiểu hóa sát thương và hướng tiến dần về đích
                priority_score = new_acc_damage + nxt_h * 0.05
                heapq.heappush(pq, (priority_score, new_acc_damage, nxt_h, nxt, path + [nxt]))
                
                if nxt != goal:
                    path_step_monitor.log_node_state(nx, ny, "open")
                    
    path_step_monitor.log_step("Expectimax: Không tìm thấy đường đi tới đích!")
    return None


def analyze_map_risk(map_manager):
    """
    Phân tích rủi ro bản đồ bằng cách duyệt qua tất cả các ô có thể đi qua (walkable cells).
    Mỗi ô đóng vai trò là một Nút cơ hội để tính toán điểm đe dọa (threat score):
    threat_score = expected_damage * (1.0 + freeze_probability)
    
    Trả về từ điển chứa tọa độ điểm nóng nguy hiểm nhất, nơi an toàn nhất, và điểm đe dọa cực đại.
    """
    max_threat = -1.0
    min_threat = float('inf')
    hotspot = None
    safest = None

    width = getattr(map_manager, 'width', 20)
    height = getattr(map_manager, 'height', 20)

    for x in range(width):
        for y in range(height):
            if not map_manager.is_obstacle(x, y):
                exp_damage = map_manager.get_expected_damage(x, y)
                freeze_prob = map_manager.get_freeze_probability(x, y)
                threat_score = exp_damage * (1.0 + freeze_prob)

                # Tìm ô có mức đe dọa cao nhất (Hotspot)
                if threat_score > max_threat or hotspot is None:
                    max_threat = threat_score
                    hotspot = (x, y)

                # Tìm ô có mức đe dọa thấp nhất (Safest)
                if threat_score < min_threat or safest is None:
                    min_threat = threat_score
                    safest = (x, y)

    hotspot_damage = map_manager.get_expected_damage(hotspot[0], hotspot[1]) if hotspot else 0.0
    hotspot_freeze = map_manager.get_freeze_probability(hotspot[0], hotspot[1]) if hotspot else 0.0
    safest_damage = map_manager.get_expected_damage(safest[0], safest[1]) if safest else 0.0
    safest_freeze = map_manager.get_freeze_probability(safest[0], safest[1]) if safest else 0.0

    path_step_monitor.log_step("=== PHÂN TÍCH RỦI RO BẢN ĐỒ (EXPECTIMAX CHANCE NODES) ===")
    path_step_monitor.log_step(f"Điểm Nóng Nguy Hiểm Nhất (Hotspot): Tọa độ {hotspot} | Mức đe dọa: {max_threat:.2f} (Sát thương: {hotspot_damage:.2f}, Tỷ lệ đóng băng: {hotspot_freeze*100:.1f}%)")
    path_step_monitor.log_step(f"Nơi Trú Ẩn An Toàn Nhất (Safest Haven): Tọa độ {safest} | Mức đe dọa: {min_threat:.2f} (Sát thương: {safest_damage:.2f}, Tỷ lệ đóng băng: {safest_freeze*100:.1f}%)")
    
    if max_threat > 0:
        path_step_monitor.log_step(f"Lời khuyên cho Creep: Ưu tiên di chuyển qua các vùng an toàn gần {safest} và tuyệt đối né tránh hotspot tại {hotspot}.")
    else:
        path_step_monitor.log_step("Lời khuyên cho Creep: Không phát hiện tháp phòng thủ gây đe dọa, di chuyển tự do.")

    return {
        "hotspot": hotspot,
        "safest": safest,
        "max_threat": max_threat if max_threat >= 0 else 0.0
    }


def select_best_path_from_candidates(candidate_paths, map_manager):
    """
    Đánh giá một danh sách các đường đi khả thi (sinh ra bởi các giải thuật khác)
    bằng cách áp dụng mô hình Nút cơ hội Expectimax để chọn ra đường đi tối ưu nhất (ít mất máu nhất).
    Trả về: (đường_đi_tối_ưu, sát_thương_kỳ_vọng, hp_còn_lại_dự_kiến, chỉ_số_đường_đi)
    """
    if not candidate_paths:
        return None, 0.0, 0.0

    path_step_monitor.log_step(f"=== EXPECTIMAX EVALUATOR: ĐÁNH GIÁ {len(candidate_paths)} ĐƯỜNG ĐÍ KHẢ THI ===")

    best_path = None
    min_expected_damage = float('inf')
    best_hp = 0.0
    best_index = -1

    for idx, path in enumerate(candidate_paths):
        acc_damage = 0.0
        for px, py in path:
            if (px, py) == map_manager.start:
                continue
            base_dmg = map_manager.get_expected_damage(px, py)
            freeze_prob = map_manager.get_freeze_probability(px, py)
            expected_step_dmg = base_dmg * (1.0 + freeze_prob)
            acc_damage += expected_step_dmg + 0.001  # Chi phí bước đi nhỏ làm tiêu chí phá vỡ thế cân bằng

        remaining_hp = max(0.0, 100.0 - acc_damage)

        if acc_damage < min_expected_damage:
            min_expected_damage = acc_damage
            best_path = path
            best_hp = remaining_hp
            best_index = idx + 1

    if best_path:
        path_step_monitor.log_step(
            f"🏆 Expectimax đã chọn ĐƯỜNG ĐÍ SỐ {best_index}/{len(candidate_paths)} là đường tối ưu nhất (ít tốn máu nhất)! "
            f"Độ dài: {len(best_path)} ô | Sát thương kỳ vọng: {min_expected_damage:.1f} | HP còn lại dự kiến: {best_hp:.1f}/100"
        )

    return best_path, min_expected_damage, best_hp, best_index
