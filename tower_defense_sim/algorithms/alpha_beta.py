import path_step_monitor

def solve(start, goal, map_manager, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy ALPHA-BETA PRUNING từ {start}")
    
    MAX_DEPTH = 5 
    best_moves = {}

    def alphabeta(state, depth, alpha, beta, is_maximizer):
        # 1. Điều kiện dừng: Đạt độ sâu tối đa hoặc chạm đích
        if depth == 0 or state == goal:
            damage = map_manager.get_expected_damage(state[0], state[1])
            # Điểm số tối ưu: Sát thương càng thấp thì điểm càng cao
            return 100.0 - damage

        # 2. Tầng MAX (Người chơi tìm cách tối đa hóa điểm số / Né sát thương)
        if is_maximizer:
            value = float('-inf')
            actions = map_manager.get_neighbors(state[0], state[1])
            if not actions:
                return 0.0
                
            best_action = actions[0]
            for action in actions:
                next_val = alphabeta(action, depth - 1, alpha, beta, False)
                if next_val > value:
                    value = next_val
                    best_action = action
                
                # Cập nhật Alpha
                alpha = max(alpha, value)
                # Điều kiện cắt tỉa Beta
                if alpha >= beta:
                    break
            
            best_moves[state] = best_action
            return value
            
        # 3. Tầng MIN (Đối thủ hoặc môi trường tìm cách giảm điểm số của bạn)
        else:
            value = float('inf')
            # Ở môi trường đối kháng, ta lấy các bước đi có thể xảy ra từ trạng thái hiện tại
            actions = map_manager.get_neighbors(state[0], state[1])
            if not actions:
                return 0.0
                
            for action in actions:
                next_val = alphabeta(action, depth - 1, alpha, beta, True)
                if next_val < value:
                    value = next_val
                
                # Cập nhật Beta
                beta = min(beta, value)
                # Điều kiện cắt tỉa Alpha
                if alpha >= beta:
                    break
                    
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
        
    if path[-1] == goal:
        path_step_monitor.log_step(f"Alpha-Beta: Tìm thấy đường đi tối ưu dài {len(path)} ô.")
        return path
    return None