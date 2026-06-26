from collections import deque
import time
import path_step_monitor

def solve(start, goal, grid, delay=0.0):
    path_step_monitor.log_step(f"Bắt đầu thuật toán BFS từ {start} đến {goal}")
    
    node = start
    
    if node == goal:
        return [node]
        
    frontier = deque([node])
    frontier_states = {node}
    
    reached = {node}
    
    parent = {start: None}
    
    while frontier:
        node = frontier.popleft()
        frontier_states.remove(node)
        
        path_step_monitor.log_node_state(node[0], node[1], "closed")
        path_step_monitor.log_step(f"Mở node (BFS): {node}")
        
        if delay > 0:
            time.sleep(delay)
            
        neighbors = grid.get_neighbors(node[0], node[1])
        for child in neighbors:
            if child not in reached and child not in frontier_states:
                parent[child] = node
                
                if child == goal:
                    path = []
                    curr = child
                    while curr is not None:
                        path.append(curr)
                        curr = parent[curr]
                    path.reverse()
                    
                    for px, py in path:
                        if (px, py) != start and (px, py) != goal:
                            path_step_monitor.log_node_state(px, py, "path")
                    return path
                    
                reached.add(child)
                
                frontier.append(child)
                frontier_states.add(child)
                
                path_step_monitor.log_node_state(child[0], child[1], "open")
                path_step_monitor.log_step(f"Khám phá neighbor (BFS): {child}")
                
                if delay > 0:
                    time.sleep(delay * 0.5)
                    
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None
