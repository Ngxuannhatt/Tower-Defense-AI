from .node import Node

def get_misplaced_count(self, matrix):
    """Hàm h(n): Tính số ô còn rác trên ma trận hiện tại."""
    return sum(row.count(1) for row in matrix)

def get_vacuum_neighbors(self, curr):
    """
    Hàm sinh các node con từ node hiện tại n.
    Trả về danh sách tuple: (child_node, cost_n_m)
    Mỗi hành động mặc định có chi phí là 1.
    """
    possible_moves = []
    r, c = curr.x, curr.y
    
    # 1. Hành động Di chuyển (Lên, Xuống, Trái, Phải)
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < self.n and 0 <= nc < self.n:
            child = Node(nr, nc, curr.matrix, parent=curr, action=f"Đi tới ({nr},{nc})")
            possible_moves.append((child, 1))
            
    # 2. Hành động Hút rác (Chỉ thực hiện khi ô hiện tại có rác)
    if curr.matrix[r][c] == 1:
        new_mat = [row[:] for row in curr.matrix]
        new_mat[r][c] = 0
        child = Node(r, c, new_mat, parent=curr, action=f"Hút rác tại ({r},{c})")
        possible_moves.append((child, 1))
        
    return possible_moves

def IDAstar(self):
    """
    Thuật toán IDA* biến thể: Duyệt theo ngưỡng I_0 tăng dần.
    Ngưỡng cập nhật: I_0 = I_0 + min(g(n_con)) của các node con được sinh ra.
    """
    # Khởi tạo node gốc
    root_node = Node(self.agent_x, self.agent_y, self.matrix, parent=None, action=f"Bắt đầu tại ({self.agent_x},{self.agent_y})")
    start_key = root_node.get_state_key()
    
    h_start = get_misplaced_count(self, root_node.matrix)
    g_start = 0
    
    # Ngưỡng ban đầu I_0 = f(Start) = g(Start) + h(Start) 
    I_0 = g_start + h_start
    
    # Cấu trúc FRONTIER lưu kèm thông tin: { state_key: (f_value, g_value, node_object) }
    FRONTIER = {start_key: (I_0, g_start, root_node)}
    REACHED = {}
    
    steps_limit = 0
    
    while FRONTIER:
        steps_limit += 1
        if steps_limit > 50000:
            return None
            
        # Chọn node n trong FRONTIER có f(n) nhỏ nhất 
        n_key = min(FRONTIER, key=lambda k: FRONTIER[k][0])
        f_curr, g_curr, curr_node = FRONTIER[n_key]
        
        # Kiểm tra điều kiện dừng / Đích 
        if curr_node.is_goal() or get_misplaced_count(self, curr_node.matrix) == 0:
            path = []
            temp = curr_node
            while temp is not None:
                path.append(temp)
                temp = temp.parent
            path.reverse()
            return path
            
        # Xóa khỏi FRONTIER và đưa vào REACHED [cite: 26]
        del FRONTIER[n_key]
        REACHED[n_key] = g_curr
        
        # Sinh các node con kề m 
        neighbors = get_vacuum_neighbors(self, curr_node)
        if not neighbors:
            continue
            
        # Thu thập danh sách các g(m) của các node con để tìm min(g(n)) theo ý bạn
        g_children_costs = []
        valid_children = []
        
        for child, cost_n_m in neighbors:
            m_key = child.get_state_key()
            g_new_m = g_curr + cost_n_m
            h_new_m = get_misplaced_count(self, child.matrix)
            f_new_m = g_new_m + h_new_m
            
            # Kiểm tra trùng lặp để tránh vòng lặp vô hạn
            if m_key in REACHED and g_new_m >= REACHED[m_key]:
                continue
            if m_key in FRONTIER and g_new_m >= FRONTIER[m_key][1]:
                continue
                
            g_children_costs.append(g_new_m)
            valid_children.append((m_key, f_new_m, g_new_m, child))
            
        # Nếu từ node hiện tại sinh ra được các node con hợp lệ
        if valid_children:
            min_g_child = min(g_children_costs) # Lấy g(n) nhỏ nhất trong các node con vừa sinh ra
            
            for m_key, f_new_m, g_new_m, child in valid_children:
                # Nếu f(m) nhỏ hơn hoặc bằng ngưỡng I_0 hiện tại -> Chấp nhận và đẩy vào FRONTIER 
                if f_new_m <= I_0:
                    FRONTIER[m_key] = (f_new_m, g_new_m, child)
                else:
                    # Nếu vượt ngưỡng, tiến hành cập nhật lại ngưỡng I_0 như bạn mô tả 
                    # I_0 = I_0 + min(g(n_con))
                    I_0 = I_0 + min_g_child
                    
                    # Sau khi nới rộng ngưỡng I_0, kiểm tra lại xem node này đã thỏa mãn chưa
                    if f_new_m <= I_0:
                        FRONTIER[m_key] = (f_new_m, g_new_m, child)

    return None