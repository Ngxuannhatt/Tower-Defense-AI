import copy

def forward_checking_coloring(neighbors, num_colors, callback=None):
    """
    Thuật toán Backtracking kết hợp Forward Checking để tô màu đồ thị.
    - neighbors: dict kề danh sách vùng kề nhau, ví dụ: {'A': ['B', 'C']}
    - num_colors: số lượng màu tối đa được thử nghiệm ở lượt này.
    - callback: optional function called at each assignment, domain check, or backtrack step.
                Signature: callback(region, color, action_type, assignment, domains)
    """
    regions = list(neighbors.keys())
    
    # 1. Khởi tạo Miền giá trị (Domain) ban đầu cho tất cả các vùng
    # Mỗi vùng ban đầu đều có thể nhận tất cả các màu từ 1 đến num_colors
    domains = {region: list(range(1, num_colors + 1)) for region in regions}
    
    assignment = {}  # Cấu trúc lưu kết quả gán màu hoàn chỉnh

    def backtrack(index, current_domains):
        # Nếu đã gán màu hết cho các biến (Complete Assignment)
        if index == len(regions):
            return True
            
        region = regions[index]  # Chọn biến tiếp theo chưa gán giá trị
        
        # Thử từng màu còn sót lại trong Miền giá trị (Domain) của vùng này
        for color in list(current_domains[region]):
            assignment[region] = color
            
            # --- BƯỚC FORWARD CHECKING (CẬP NHẬT DOMAIN) ---
            # Tạo một bản sao sâu của domains hiện tại để chuẩn bị lọc giá trị
            next_domains = copy.deepcopy(current_domains)
            is_valid_step = True
            
            # Duyệt qua các vùng kề của vùng vừa được gán màu
            for neighbor in neighbors[region]:
                # Chỉ lọc domain của những vùng kề CHƯA được gán màu chính thức
                if neighbor not in assignment:
                    if color in next_domains[neighbor]:
                        next_domains[neighbor].remove(color)  # Xóa màu trùng khỏi miền giá trị
                    
                    # RÀNG BUỘC SỚM: Nếu domain của vùng kề bị rỗng (ko còn màu nào để chọn)
                    # thì nhánh gán màu này chắc chắn thất bại -> Hủy bước và kiểm tra màu khác ngay
                    if not next_domains[neighbor]:
                        is_valid_step = False
                        break
            
            # Gọi callback báo cáo gán màu và trạng thái domain sau lọc
            if callback:
                action = "ASSIGN" if is_valid_step else "FAIL_FC"
                callback(region, color, action, assignment.copy(), copy.deepcopy(next_domains))

            # Nếu bước Forward Checking thấy hợp lệ, tiến hành gọi đệ quy
            if is_valid_step:
                if backtrack(index + 1, next_domains):
                    return True
            
            # QUAY LUI: Trả lại trạng thái nếu nhánh đi này không dẫn đến lời giải
            del assignment[region]
            if callback:
                callback(region, None, "BACKTRACK", assignment.copy(), copy.deepcopy(current_domains))
            
        return False

    if backtrack(0, domains):
        return assignment
    return None


def find_minimal_coloring_fc(neighbors, callback=None):
    """
    Hàm tìm kiếm số lượng màu tối thiểu đáp ứng ràng buộc sử dụng Forward Checking.
    Tăng dần số lượng màu bắt đầu từ 1.
    """
    if not neighbors:
        return {}, 0
        
    num_regions = len(neighbors)
    for num_colors in range(1, num_regions + 1):
        solution = forward_checking_coloring(neighbors, num_colors, callback)
        if solution is not None:
            return solution, num_colors
            
    return None, 0