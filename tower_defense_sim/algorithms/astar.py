import heapq
import time
import path_step_monitor

class AStarNode:
    """
    Lớp biểu diễn một nút trong không gian tìm kiếm A*.
    Mỗi nút lưu trữ tọa độ, nút cha, và các thành phần chi phí:
    - g: Chi phí thực tế đi từ điểm bắt đầu đến nút hiện tại.
    - h: Chi phí ước lượng (Heuristic) từ nút hiện tại đến đích.
    - f: Tổng chi phí ước tính (f = g + h).
    """
    def __init__(self, position, parent=None, g=0.0, h=0.0):
        self.position = position
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h

    @property
    def g_cost(self):
        return self.g

    @g_cost.setter
    def g_cost(self, val):
        self.g = val

    @property
    def h_cost(self):
        return self.h

    @h_cost.setter
    def h_cost(self, val):
        self.h = val

    @property
    def f_cost(self):
        return self.f

    @f_cost.setter
    def f_cost(self, val):
        self.f = val

    def __lt__(self, other):
        # Bộ phá vỡ thế cân bằng (tie-breaker): Nếu tổng chi phí f bằng nhau,
        # thuật toán ưu tiên nút có g lớn hơn (tức là nút đi sâu hơn, gần đích hơn)
        # nhằm giảm thiểu số lượng nút phải duyệt thừa.
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f

def solve(start, goal, grid, delay=0.0):
    """
    Giải thuật tìm kiếm A* (A-Star).
    - Kết hợp chi phí thực tế g(n) và ước lượng heuristic h(n) để định hướng tìm đường tối ưu nhất.
    - Sử dụng hàm Heuristic là khoảng cách Manhattan (phù hợp với lưới ô vuông di chuyển 4 hướng).
    """
    path_step_monitor.log_step(f"Bắt đầu thuật toán A* từ {start} đến {goal}")
    
    # Khoảng cách Manhattan từ Start đến Goal
    start_h = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    start_node = AStarNode(start, parent=None, g=0.0, h=start_h)
    
    # Hàng đợi ưu tiên lưu các nút đang chờ duyệt (Open list)
    FRONTIER = [start_node]
    
    # Từ điển lưu các nút đã đi qua tối ưu nhất (Closed list/Reached set)
    REACHED = {}
    
    path_step_monitor.log_node_state(start[0], start[1], "open")
    
    while FRONTIER:
        # Lấy nút có giá trị f nhỏ nhất ra khỏi Open list (FRONTIER)
        n_node = heapq.heappop(FRONTIER)
        n = n_node.position
        
        # Nếu tọa độ này đã được tiếp cận trước đó với đường đi ngắn hơn/tốt hơn, bỏ qua
        if n in REACHED and REACHED[n].g <= n_node.g:
            continue
            
        # Ghi nhận nút đã duyệt tối ưu nhất
        REACHED[n] = n_node
        path_step_monitor.log_node_state(n[0], n[1], "closed")
        path_step_monitor.log_step(f"Mở node: {n}, cost: {n_node.g}, total_cost: {n_node.f}")
        
        if delay > 0:
            time.sleep(delay)
            
        # Khi tìm thấy đích, thực hiện truy vết ngược qua parent để lấy đường đi hoàn chỉnh
        if n == goal:
            path_step_monitor.log_step(f"Đã tìm thấy đường đi tới đích {goal}!")
            path = []
            curr = n_node
            while curr:
                path.append(curr.position)
                curr = curr.parent
            path.reverse()
            
            # Cập nhật trạng thái hiển thị đường đi trên GUI
            for px, py in path:
                if (px, py) != start and (px, py) != goal:
                    path_step_monitor.log_node_state(px, py, "path")
            return path
            
        # Duyệt qua các nút lân cận hợp lệ
        neighbors = grid.get_neighbors(n[0], n[1])
        for m in neighbors:
            g_new = n_node.g + 1.0 # Chi phí bước đi tăng 1 đơn vị
            h_m = abs(m[0] - goal[0]) + abs(m[1] - goal[1]) # Ước lượng khoảng cách Manhattan từ hàng xóm đến đích
            f_m = g_new + h_m
            
            # Trường hợp 1: Ô hàng xóm 'm' nằm trong tập REACHED (đã được duyệt)
            if m in REACHED:
                m_reached_node = REACHED[m]
                # Nếu đường đi mới không tốt hơn đường cũ, bỏ qua
                if g_new >= m_reached_node.g:
                    continue
                else:
                    # Nếu đường đi mới ngắn hơn, rút 'm' khỏi REACHED (Reopen)
                    # và đẩy lại vào FRONTIER để cập nhật các nút con của nó
                    del REACHED[m]
                    m_reached_node.g = g_new
                    m_reached_node.f = f_m
                    m_reached_node.parent = n_node
                    heapq.heappush(FRONTIER, m_reached_node)
                    
                    path_step_monitor.log_node_state(m[0], m[1], "open")
                    path_step_monitor.log_step(f"Cập nhật Heuristic (Reopen) cho {m}: g={g_new}, h={h_m}, f={f_m}")
                    if delay > 0:
                        time.sleep(delay * 0.5)
            
            # Trường hợp 2: Ô hàng xóm 'm' đã nằm trong danh sách chờ duyệt (FRONTIER)
            else:
                m_frontier_node = next((node for node in FRONTIER if node.position == m), None)
                if m_frontier_node:
                    # Nếu tìm thấy đường đi mới tới 'm' có chi phí rẻ hơn
                    if g_new < m_frontier_node.g:
                        m_frontier_node.g = g_new
                        m_frontier_node.f = f_m
                        m_frontier_node.parent = n_node
                        # Tổ chức lại cấu trúc cây Heap sau khi cập nhật giá trị nút con
                        heapq.heapify(FRONTIER)
                        
                        path_step_monitor.log_step(f"Cập nhật Heuristic cho {m} trong FRONTIER: g={g_new}, h={h_m}, f={f_m}")
                        if delay > 0:
                            time.sleep(delay * 0.5)
                
                # Trường hợp 3: Ô hàng xóm 'm' hoàn toàn mới (chưa từng thấy)
                else:
                    m_node = AStarNode(m, parent=n_node, g=g_new, h=h_m)
                    heapq.heappush(FRONTIER, m_node)
                    
                    path_step_monitor.log_node_state(m[0], m[1], "open")
                    path_step_monitor.log_step(f"Cập nhật Heuristic cho {m}: g={g_new}, h={h_m}, f={f_m}")
                    if delay > 0:
                        time.sleep(delay * 0.5)
                        
    path_step_monitor.log_step("Không tìm thấy đường đi khả thi!")
    return None
