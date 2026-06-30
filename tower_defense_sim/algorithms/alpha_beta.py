import time
import path_step_monitor

def solve(start, goal, map_manager, delay=0.0):
    """
    Giải thuật Tìm kiếm Đối kháng có cắt tỉa Alpha-Beta (Alpha-Beta Pruning).
    - Giúp tối ưu hóa thuật toán Minimax bằng cách bỏ qua các nhánh con không làm thay đổi kết quả cuối cùng.
    - Hai tham số điều kiện cắt tỉa:
      * Alpha (alpha): Lưu trữ điểm số tốt nhất (lớn nhất) mà người chơi Maximizer có thể đảm bảo từ đầu. Khởi tạo = -Vô cùng.
      * Beta (beta): Lưu trữ điểm số tốt nhất (nhỏ nhất) mà đối thủ Minimizer có thể đảm bảo từ đầu. Khởi tạo = +Vô cùng.
    - Quy tắc cắt tỉa: Khi ta phát hiện alpha >= beta ở một nút, dừng duyệt toàn bộ các nhánh con còn lại
      của nút đó vì đối thủ thông minh sẽ không bao giờ để ta đi vào nhánh này.
    - Điểm số: 100.0 - Sát thương dự kiến (Sát thương càng thấp thì điểm số càng cao, phù hợp cho quái né tháp).
    """
    path_step_monitor.log_step(f"=== Khởi chạy ALPHA-BETA PRUNING từ {start} đến {goal} ===")
    
    MAX_DEPTH = 5 
    best_moves = {}
    explored_states = set()

    def alphabeta(state, depth, alpha, beta, is_maximizer):
        # Trực quan hóa nút đang được khám phá trên GUI
        if state not in explored_states:
            explored_states.add(state)
            path_step_monitor.log_node_state(state[0], state[1], "closed" if is_maximizer else "open")
            if delay > 0:
                time.sleep(delay)

        # 1. Điều kiện dừng: Chạm đích hoặc đạt tới giới hạn độ sâu tối đa
        if depth == 0 or state == goal:
            damage = map_manager.get_expected_damage(state[0], state[1])
            # Điểm số tối ưu: Điểm càng cao khi sát thương càng nhỏ
            score = 100.0 - damage
            path_step_monitor.log_step(
                f"[Tầng {'MAX' if is_maximizer else 'MIN'}] Đạt điều kiện dừng tại {state} (độ sâu còn lại: {depth}). "
                f"Sát thương dự kiến: {damage:.1f}, Điểm: {score:.1f}"
            )
            return score

        # 2. Tầng MAX (Người chơi/Quái vật - cố gắng chọn nước đi có điểm số tối đa/né tháp)
        if is_maximizer:
            value = float('-inf')
            actions = map_manager.get_neighbors(state[0], state[1])
            if not actions:
                path_step_monitor.log_step(f"[Tầng MAX] Trạng thái {state} không có nước đi kế tiếp. Trả về 0.0")
                return 0.0
                
            path_step_monitor.log_step(
                f"[Tầng MAX] Trạng thái {state}, độ sâu={depth}, alpha={alpha:.1f}, beta={beta:.1f}. "
                f"Các nước đi khả thi: {actions}"
            )
            
            best_action = actions[0]
            for action in actions:
                path_step_monitor.log_step(f"  └─ Maximizer thử đi tới {action}...")
                next_val = alphabeta(action, depth - 1, alpha, beta, False)
                path_step_monitor.log_step(f"  └─ Maximizer kết quả từ {action}: {next_val:.1f}")
                
                # Cập nhật giá trị lớn nhất tìm thấy
                if next_val > value:
                    value = next_val
                    best_action = action
                
                # Cập nhật ngưỡng Alpha của tầng MAX
                alpha = max(alpha, value)
                path_step_monitor.log_step(f"  └─ Cập nhật alpha = {alpha:.1f} tại {state}")
                
                # RÀNG BUỘC CẮT TỈA BETA: Nếu điểm MAX có thể chọn (alpha) lớn hơn hoặc bằng
                # điểm tốt nhất MIN có thể chặn (beta), dừng duyệt ngay lập tức.
                if alpha >= beta:
                    path_step_monitor.log_step(
                        f"  ✂️ [Cắt tỉa BETA] tại {state}: alpha={alpha:.1f} >= beta={beta:.1f}. Dừng duyệt nhánh này!"
                    )
                    break
            
            best_moves[state] = best_action
            path_step_monitor.log_step(f"[Tầng MAX] Trực giác tốt nhất tại {state} là đi tới {best_action} với điểm số {value:.1f}")
            return value
            
        # 3. Tầng MIN (Môi trường/Các tháp phòng thủ - cố gắng giảm tối đa điểm số/gây sát thương tối đa)
        else:
            value = float('inf')
            actions = map_manager.get_neighbors(state[0], state[1])
            if not actions:
                path_step_monitor.log_step(f"[Tầng MIN] Trạng thái {state} không có nước đi lân cận. Trả về 0.0")
                return 0.0
                
            path_step_monitor.log_step(
                f"[Tầng MIN] Trạng thái {state}, độ sâu={depth}, alpha={alpha:.1f}, beta={beta:.1f}. "
                f"Môi trường phân tích các hướng đi: {actions}"
            )
            
            for action in actions:
                path_step_monitor.log_step(f"  └─ Minimizer giả lập đi tới {action}...")
                next_val = alphabeta(action, depth - 1, alpha, beta, True)
                path_step_monitor.log_step(f"  └─ Minimizer kết quả từ {action}: {next_val:.1f}")
                
                # Cập nhật giá trị nhỏ nhất tìm thấy
                if next_val < value:
                    value = next_val
                
                # Cập nhật ngưỡng Beta của tầng MIN
                beta = min(beta, value)
                path_step_monitor.log_step(f"  └─ Cập nhật beta = {beta:.1f} tại {state}")
                
                # RÀNG BUỘC CẮT TỈA ALPHA: Nếu điểm tốt nhất của MIN bị hạ xuống dưới alpha, cắt tỉa ngay.
                if alpha >= beta:
                    path_step_monitor.log_step(
                        f"  ✂️ [Cắt tỉa ALPHA] tại {state}: alpha={alpha:.1f} >= beta={beta:.1f}. Dừng duyệt nhánh này!"
                    )
                    break
                    
            path_step_monitor.log_step(f"[Tầng MIN] Điểm số tối thiểu môi trường đè bẹp tại {state} là {value:.1f}")
            return value

    # Khởi chạy đệ quy Alpha-Beta từ Start, độ sâu MAX_DEPTH, alpha=-Vô cùng, beta=+Vô cùng
    alphabeta(start, MAX_DEPTH, float('-inf'), float('inf'), True)
    
    # --- Truy vết ngược lại đường đi tốt nhất dựa trên best_moves ---
    path = [start]
    curr = start
    while curr != goal and len(path) < 100:
        nxt = best_moves.get(curr)
        # Nếu không tìm thấy nước đi tiếp theo hoặc bị lặp vòng
        if not nxt or nxt in path:
            neighbors = map_manager.get_neighbors(curr[0], curr[1])
            if neighbors:
                # Thuật toán dự phòng (Fallback): Chọn ô gần đích nhất theo khoảng cách Manhattan
                nxt = min(neighbors, key=lambda c: abs(c[0]-goal[0]) + abs(c[1]-goal[1]))
            else:
                break
        path.append(nxt)
        path_step_monitor.log_node_state(nxt[0], nxt[1], "closed")
        curr = nxt
        if delay > 0:
            time.sleep(delay * 0.5)
        
    if path[-1] == goal:
        path_step_monitor.log_step(f"Alpha-Beta: Tìm thấy đường đi tối ưu dài {len(path)} ô.")
        for px, py in path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return path
    
    path_step_monitor.log_step("Alpha-Beta: Không tìm thấy đường đi an toàn tới đích.")
    return None