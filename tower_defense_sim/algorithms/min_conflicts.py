import random
import time
from algorithms import astar
import path_step_monitor

class CSP:
    """
    Lớp biểu diễn bài toán thỏa mãn ràng buộc (CSP - Constraint Satisfaction Problem).
    - variables: Các biến cần gán giá trị (ở đây là danh sách tháp: T0, T1, ..., T17).
    - domains: Miền giá trị cho từng biến (tất cả các ô tọa độ trống hợp lệ trên bản đồ).
    - map_manager: Quản lý lưới bản đồ để cập nhật vị trí tháp phòng thủ.
    """
    def __init__(self, map_manager, variables, domains):
        self.map_manager = map_manager
        self.variables = variables
        self.domains = domains

def get_conflicts(var, v, current, csp):
    """
    Tính toán số lượng xung đột (hoặc điểm phạt) khi gán vị trí 'v' cho biến tháp 'var'.
    Các loại xung đột/ràng buộc được lượng hóa bằng trọng số:
    1. Trùng vị trí với các tháp khác (overlap): Phạt +500 điểm.
    2. Đặt tháp lên điểm xuất phát (Start) hoặc điểm đích (Goal): Phạt +1000 điểm.
    3. Tháp chặn hoàn toàn đường đi từ Start đến Goal (Ràng buộc cứng): Phạt +100 điểm.
    """
    conflicts = 0
    
    # 1. Kiểm tra chồng lấn tọa độ với các tháp khác đã gán
    for other_var, other_val in current.items():
        if other_var != var and other_val == v:
            conflicts += 500
            
    # 2. Kiểm tra đặt tháp đè lên điểm xuất phát hoặc đích
    if v == csp.map_manager.start or v == csp.map_manager.goal:
        conflicts += 1000
        
    # 3. Kiểm tra ràng buộc cứng: Chặn lối đi của quái.
    # Tạm thời xây dựng lại cấu hình bản đồ lưới với vị trí thử nghiệm mới này để chạy thử A*
    csp.map_manager.reset()
    for other_var, other_val in current.items():
        if other_var != var:
            csp.map_manager.add_tower(other_val[0], other_val[1], "Basic")
    csp.map_manager.add_tower(v[0], v[1], "Basic")
    
    # Chạy thuật toán A* ẩn (không log ra GUI) để xem quái có tìm được đường về đích không
    was_silenced = path_step_monitor.is_silenced()
    path_step_monitor.set_silenced(True)
    path = astar.solve(csp.map_manager.start, csp.map_manager.goal, csp.map_manager, delay=0.0)
    path_step_monitor.set_silenced(was_silenced)
    
    # Nếu không tìm thấy đường đi (đường bị tháp chặn hoàn toàn), ghi nhận xung đột
    if not path:
        conflicts += 100
        
    return conflicts

def min_conflicts(csp, max_steps, update_ui_callback=None, log_callback=None):
    """
    Thuật toán Min-Conflicts tối ưu hóa tìm kiếm cục bộ để giải bài toán CSP.
    - Bước 1: Khởi tạo một phép gán hoàn tất ngẫu nhiên (gán bừa tọa độ cho 18 tháp).
    - Bước 2: Ở mỗi bước lặp, tìm các tháp đang bị lỗi/xung đột (vi phạm ràng buộc).
    - Bước 3: Nếu không còn tháp nào bị lỗi -> Bài toán đã được giải thành công! Trả về kết quả.
    - Bước 4: Nếu vẫn còn tháp lỗi, chọn ngẫu nhiên một tháp bị lỗi và di chuyển nó tới ô
              trong miền giá trị mà tại đó số lượng xung đột là ít nhất (minimized conflicts).
    """
    # 1. Tạo phép gán ngẫu nhiên ban đầu cho tất cả các tháp
    current = {}
    for var in csp.variables:
        current[var] = random.choice(csp.domains[var])
        
    # Đặt tháp lên bản đồ theo phép gán ngẫu nhiên ban đầu
    csp.map_manager.reset()
    for var, val in current.items():
        csp.map_manager.add_tower(val[0], val[1], "Basic")
        
    if update_ui_callback:
        update_ui_callback()
        
    for step in range(1, max_steps + 1):
        # Xác định tất cả các tháp đang bị lỗi/xung đột
        conflicted_vars = []
        for var in csp.variables:
            val = current[var]
            if get_conflicts(var, val, current, csp) > 0:
                conflicted_vars.append(var)
                
        # Nếu không còn tháp nào bị lỗi -> Xếp tháp thành công hoàn mỹ!
        if not conflicted_vars:
            if log_callback:
                log_callback(f"Min-Conflicts: Đã tìm thấy cấu hình hợp lệ tại bước {step}!")
            return current
            
        # Chọn ngẫu nhiên một tháp đang bị lỗi để sửa vị trí
        var = random.choice(conflicted_vars)
        
        # Tìm vị trí trong miền giá trị giúp giảm xung đột cho tháp này nhiều nhất
        best_val = current[var]
        min_conf = get_conflicts(var, best_val, current, csp)
        
        # Lấy mẫu ngẫu nhiên tối đa 50 ô trống trong miền giá trị để tính toán nhanh, tránh lag GUI
        domain_sample = random.sample(csp.domains[var], min(50, len(csp.domains[var])))
        if current[var] not in domain_sample:
            domain_sample.append(current[var])
            
        for v in domain_sample:
            conf = get_conflicts(var, v, current, csp)
            # Nếu tìm thấy vị trí mới ít lỗi hơn vị trí cũ, ghi nhận lại
            if conf < min_conf:
                min_conf = conf
                best_val = v
                
        # Cập nhật tọa độ mới cho tháp
        current[var] = best_val
        
        # Vẽ lại cấu hình tháp mới lên bản đồ
        csp.map_manager.reset()
        for v_name, v_coord in current.items():
            csp.map_manager.add_tower(v_coord[0], v_coord[1], "Basic")
            
        if log_callback:
            log_callback(f"🔄 Bước {step}/{max_steps} | Tháp: {var} -> {best_val} | Số tháp lỗi: {len(conflicted_vars)}")
            
        if update_ui_callback:
            update_ui_callback()
            
        time.sleep(0.04)
        
    if log_callback:
        log_callback(f"Kết thúc {max_steps} bước nhưng chưa tìm được cấu hình hoàn hảo không lỗi.")
    return current

def run_min_conflicts(map_manager, num_towers=18, max_steps=100, update_ui_callback=None, log_callback=None):
    """
    Hàm chính chạy giải thuật Min-Conflicts CSP khởi chạy từ giao diện GUI.
    - Khởi tạo 18 biến tháp (T0 -> T17).
    - Định nghĩa miền giá trị là tất cả ô không phải Start/Goal.
    - Sau khi tìm được cấu hình không chặn đường đi hợp lệ, gán ngẫu nhiên loại tháp (Basic, Ice, Fire)
      để tăng tính đa dạng mỹ thuật cho mê cung tháp.
    """
    if log_callback:
        log_callback("Khởi tạo cấu hình tháp ngẫu nhiên ban đầu cho CSP Min-Conflicts...")
        
    variables = [f"T{i}" for i in range(num_towers)]
    domain = []
    for x in range(map_manager.width):
        for y in range(map_manager.height):
            if (x, y) != map_manager.start and (x, y) != map_manager.goal:
                domain.append((x, y))
                
    domains = {var: domain for var in variables}
    csp = CSP(map_manager, variables, domains)
    
    final_assignment = min_conflicts(csp, max_steps, update_ui_callback, log_callback)
    
    # Đa dạng hóa các loại tháp (Basic, Ice, Fire) ở kết quả cuối cùng để tăng tính trực quan
    types = ["Basic", "Ice", "Fire"]
    map_manager.reset()
    for var, val in final_assignment.items():
        map_manager.add_tower(val[0], val[1], random.choice(types))
        
    if update_ui_callback:
        update_ui_callback()
        
    return final_assignment
