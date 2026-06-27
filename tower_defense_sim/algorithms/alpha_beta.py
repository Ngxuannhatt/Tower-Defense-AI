import time
import path_step_monitor

def solve(start, goal, map_manager, delay=0.0):
    path_step_monitor.log_step(f"=== Khởi chạy ALPHA-BETA PRUNING từ {start} đến {goal} ===")
    
    MAX_DEPTH = 5 
    best_moves = {}
    explored_states = set()

    def alphabeta(state, depth, alpha, beta, is_maximizer):
        # Log node state in GUI
        if state not in explored_states:
            explored_states.add(state)
            path_step_monitor.log_node_state(state[0], state[1], "closed" if is_maximizer else "open")
            if delay > 0:
                time.sleep(delay)

        # 1. Điều kiện dừng: Đạt độ sâu tối đa hoặc chạm đích
        if depth == 0 or state == goal:
            damage = map_manager.get_expected_damage(state[0], state[1])
            # Điểm số tối ưu: Sát thương càng thấp thì điểm càng cao
            score = 100.0 - damage
            path_step_monitor.log_step(
                f"[Tầng {'MAX' if is_maximizer else 'MIN'}] Đạt điều kiện dừng tại {state} (độ sâu còn lại: {depth}). "
                f"Sát thương dự kiến: {damage:.1f}, Điểm: {score:.1f}"
            )
            return score

        # 2. Tầng MAX (Người chơi tìm cách tối đa hóa điểm số / Né sát thương)
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
                
                if next_val > value:
                    value = next_val
                    best_action = action
                
                alpha = max(alpha, value)
                path_step_monitor.log_step(f"  └─ Cập nhật alpha = {alpha:.1f} tại {state}")
                
                # Điều kiện cắt tỉa Beta
                if alpha >= beta:
                    path_step_monitor.log_step(
                        f"  ✂️ [Cắt tỉa BETA] tại {state}: alpha={alpha:.1f} >= beta={beta:.1f}. Dừng duyệt nhánh này!"
                    )
                    break
            
            best_moves[state] = best_action
            path_step_monitor.log_step(f"[Tầng MAX] Trực giác tốt nhất tại {state} là đi tới {best_action} với điểm số {value:.1f}")
            return value
            
        # 3. Tầng MIN (Đối thủ hoặc môi trường tìm cách giảm điểm số của bạn / Gây sát thương tối đa)
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
                
                if next_val < value:
                    value = next_val
                
                beta = min(beta, value)
                path_step_monitor.log_step(f"  └─ Cập nhật beta = {beta:.1f} tại {state}")
                
                # Điều kiện cắt tỉa Alpha
                if alpha >= beta:
                    path_step_monitor.log_step(
                        f"  ✂️ [Cắt tỉa ALPHA] tại {state}: alpha={alpha:.1f} >= beta={beta:.1f}. Dừng duyệt nhánh này!"
                    )
                    break
                    
            path_step_monitor.log_step(f"[Tầng MIN] Điểm số tối thiểu môi trường đè bẹp tại {state} là {value:.1f}")
            return value

    # Khởi chạy Alpha-Beta với Alpha = -vô cùng, Beta = +vô cùng
    alphabeta(start, MAX_DEPTH, float('-inf'), float('inf'), True)
    
    # --- Tái tạo đường đi từ bảng dữ liệu best_moves ---
    path = [start]
    curr = start
    while curr != goal and len(path) < 100:
        nxt = best_moves.get(curr)
        # Nếu không tìm thấy nước đi kế tiếp hoặc bị lặp vòng dữ liệu
        if not nxt or nxt in path:
            neighbors = map_manager.get_neighbors(curr[0], curr[1])
            if neighbors:
                # Thuật toán dự phòng (Fallback): Chọn ô gần đích về khoảng cách Manhattan nhất
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
        # Đánh dấu đường đi
        for px, py in path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
        return path
    
    path_step_monitor.log_step("Alpha-Beta: Không tìm thấy đường đi an toàn tới đích.")
    return None