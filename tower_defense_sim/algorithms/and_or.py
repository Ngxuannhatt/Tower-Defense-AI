import path_step_monitor

def solve(start, goal, map_manager, delay=0.0):
    path_step_monitor.log_step(f"Khởi chạy AND_OR_GRAPH_SEARCH từ {start}")
    
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
    state_count = 0
    max_states = 5000

    def or_search(state, path):
        nonlocal state_count
        state_count += 1
        if state_count > max_states or len(path) > 100:
            return None

        if goal_test(state):
            return []
            
        if state in path:
            return None
            
        actions = get_actions(state)
        for action in actions:
            result_states = get_results(state, action)
            
            plan = and_search(result_states, path + [state])
            
            if plan is not None:
                return [action, plan]
                
        return None

    def and_search(states, path):
        plans = {}
        
        for env_status, next_node in states:
            path_step_monitor.log_node_state(next_node[0], next_node[1], "open")
            
            plan_s = or_search(next_node, path)
            
            if plan_s is None:
                return None
                
            plans[(env_status, next_node)] = plan_s
            
            if path:
                parent = path[-1]
                strategy_map[(parent[0], parent[1], env_status)] = next_node
                
        return plans

    full_plan = or_search(start, [])
    
    if full_plan is not None:
        path_step_monitor.log_step("AND-OR Search: Tìm thấy kế hoạch chiến lược thành công!")
        map_manager.last_and_or_strategy = strategy_map
        
        path = [start]
        curr = start
        while curr != goal:
            nxt = strategy_map.get((curr[0], curr[1], "normal"))
            if not nxt or nxt in path: break
            path.append(nxt)
            curr = nxt
        return path
        
    path_step_monitor.log_step("AND-OR Search: Không tìm thấy chiến lược khả thi!")
    return None
