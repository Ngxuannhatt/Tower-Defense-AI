import path_step_monitor

def solve(start, goal, map_manager, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy EXPECTIMAX từ {start}")
    
    MAX_DEPTH = 5 
    best_moves = {}

    def expectimax(state, depth, is_maximizer):
        if depth == 0 or state == goal:
            damage = map_manager.get_expected_damage(state[0], state[1])
            return 100.0 - damage

        if is_maximizer:
            value = float('-inf')
            actions = map_manager.get_neighbors(state[0], state[1])
            if not actions:
                return 0.0
                
            best_action = actions[0]
            for action in actions:
                next_val = expectimax(action, depth - 1, False)
                if next_val > value:
                    value = next_val
                    best_action = action
            
            best_moves[state] = best_action
            return value
            
        else:
            value = 0
            freeze_prob = map_manager.get_freeze_probability(state[0], state[1])
            
            outcomes = []
            if freeze_prob > 0:
                outcomes.append((freeze_prob, state))
                outcomes.append((1.0 - freeze_prob, state))
            else:
                outcomes.append((1.0, state))
                
            for probability, outcome_state in outcomes:
                value += probability * expectimax(outcome_state, depth - 1, True)
                
            return value

    expectimax(start, MAX_DEPTH, True)
    
    path = [start]
    curr = start
    while curr != goal and len(path) < 100:
        nxt = best_moves.get(curr)
        if not nxt or nxt in path:
            neighbors = map_manager.get_neighbors(curr[0], curr[1])
            if neighbors:
                nxt = min(neighbors, key=lambda c: abs(c[0]-goal[0]) + abs(c[1]-goal[1]))
            else:
                break
        path.append(nxt)
        path_step_monitor.log_node_state(nxt[0], nxt[1], "closed")
        curr = nxt
        
    if path[-1] == goal:
        path_step_monitor.log_step(f"Expectimax: Tìm thấy đường né sát thương tối ưu dài {len(path)} ô.")
        return path
    return None
