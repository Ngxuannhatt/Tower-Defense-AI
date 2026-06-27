import heapq
from .node import Node

def ucs(self): 
    root_node = Node(self.agent_x, self.agent_y, self.matrix, parent=None, action=f"Bắt đầu tại ({self.agent_x},{self.agent_y})")
    
    # Tính H (số ô còn rác)
    initial_h = get_misplaced_count(self, root_node.matrix)
    
    # Priority Queue lưu: (h_value, counter, node)
    frontier = []
    counter = 0
    heapq.heappush(frontier, (initial_h, counter, root_node))
     
    reached = set()
    steps_limit = 0

    while frontier:
        curr_h, _, curr = heapq.heappop(frontier)
        
        # Kiểm tra trùng lặp sau khi POP
        state_key = curr.get_state_key()
        if state_key in reached:
            continue
        reached.add(state_key)
        
        # Kiểm tra đích
        if curr.is_goal():
            path = []
            temp = curr
            while temp is not None:
                path.append(temp)
                temp = temp.parent
            path.reverse()
            return path
            
        steps_limit += 1
        if steps_limit > 50000: # Giảm giới hạn để tránh treo UI
            return None

        # Sinh node con
        r, c = curr.x, curr.y
        possible_moves = []
        
        # 1. Di chuyển
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.n and 0 <= nc < self.n:
                possible_moves.append(Node(nr, nc, curr.matrix, parent=curr, action=f"Đi tới ({nr},{nc})"))
                
        # 2. Hút rác
        if curr.matrix[r][c] == 1:
            new_mat = [row[:] for row in curr.matrix]
            new_mat[r][c] = 0
            possible_moves.append(Node(r, c, new_mat, parent=curr, action=f"Hút rác tại ({r},{c})"))
            
        # Push tất cả vào Heap
        for child in possible_moves:
            if child.get_state_key() not in reached:
                counter += 1
                h_val = get_misplaced_count(self, child.matrix)
                heapq.heappush(frontier, (h_val, counter, child))
    
    return None

def get_misplaced_count(self, matrix):
    # Đếm số ô còn rác (1 là rác)
    return sum(row.count(1) for row in matrix)