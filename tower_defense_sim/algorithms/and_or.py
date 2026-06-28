import random
import time
import path_step_monitor

def solve(start, goal, map_manager, delay=0.0, return_all=False):
    path_step_monitor.log_step(f"Khởi chạy AND_OR_GRAPH_SEARCH từ {start}")
    
    MAX_DEPTH = 80       # Reasonable depth limit to prevent infinite/long loop wandering
    MAX_PATHS = 100      # Target maximum viable candidate paths to collect quickly
    MAX_STEPS = 50000    # Safe step limit to prevent CPU freezing on large grids
    
    def goal_test(state):
        return state == goal

    def get_actions(state):
        return map_manager.get_neighbors(state[0], state[1])

    def get_results(state, action):
        prob = map_manager.get_freeze_probability(action[0], action[1])
        if prob > 0:
            return [("slowed", action), ("normal", action)]
        else:
            return [("normal", action)]

    strategy_map = {}
    all_extracted_paths = []
    step_count = 0
    visited_visuals = set()
    
    def find_all_strategy_paths(current_node, current_path, depth):
        nonlocal step_count
        step_count += 1
        
        if len(all_extracted_paths) >= MAX_PATHS or depth >= MAX_DEPTH or step_count > MAX_STEPS:
            return
            
        if current_node == goal:
            full_p = current_path + [current_node]
            if full_p not in all_extracted_paths:
                all_extracted_paths.append(full_p)
            return

        actions = get_actions(current_node)
        # Sort actions by distance to goal to prioritize efficient paths
        actions.sort(key=lambda a: abs(a[0] - goal[0]) + abs(a[1] - goal[1]))

        for action in actions:
            if action not in current_path:
                if delay > 0 and action not in visited_visuals:
                    visited_visuals.add(action)
                    path_step_monitor.log_node_state(action[0], action[1], "open")
                    time.sleep(delay)
                    
                result_states = get_results(current_node, action)
                for env_status, nxt in result_states:
                    key = (current_node[0], current_node[1], env_status)
                    if key not in strategy_map:
                        strategy_map[key] = []
                    if nxt not in strategy_map[key]:
                        strategy_map[key].append(nxt)
                
                find_all_strategy_paths(action, current_path + [current_node], depth + 1)
                if len(all_extracted_paths) >= MAX_PATHS or step_count > MAX_STEPS:
                    break

    find_all_strategy_paths(start, [], 0)
    
    if all_extracted_paths:
        path_step_monitor.log_step(f"AND-OR Search: Tìm thấy chiến lược với {len(all_extracted_paths)} đường đi khả thi!")
        
        # Format strategy_map for single-step simulation lookup
        sim_strategy = {}
        for k, v in strategy_map.items():
            if isinstance(v, list) and len(v) > 0:
                sim_strategy[k] = v[0]
            else:
                sim_strategy[k] = v
        map_manager.last_and_or_strategy = sim_strategy
        
        if return_all:
            return all_extracted_paths

        # Highlight nodes of randomly selected path
        selected_path = random.choice(all_extracted_paths)
        path_step_monitor.log_step(f"🎲 AND-OR Search đã ngẫu nhiên chọn 1 đường đi trong số {len(all_extracted_paths)} đường khả thi!")
        for px, py in selected_path:
            if (px, py) != start and (px, py) != goal:
                path_step_monitor.log_node_state(px, py, "path")
                
        return selected_path

    path_step_monitor.log_step("AND-OR Search: Không tìm thấy chiến lược khả thi trong giới hạn an toàn!")
    return None if not return_all else []
