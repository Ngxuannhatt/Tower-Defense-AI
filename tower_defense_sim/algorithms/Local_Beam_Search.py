import random
from .node import Node

def get_heuristic(self, node):
    """
    h(n) = số rác còn lại + khoảng cách tới đống rác gần nhất
    """
    dirt_positions = []

    for i in range(self.n):
        for j in range(self.n):
            if node.matrix[i][j] == 1:
                dirt_positions.append((i, j))

    # Goal
    if not dirt_positions:
        return 0

    nearest = min(
        abs(node.x - r) + abs(node.y - c)
        for r, c in dirt_positions
    )

    return len(dirt_positions) + nearest


def get_vacuum_neighbors(self, curr):
    """
    Sinh trạng thái lân cận
    """
    possible_moves = []

    r, c = curr.x, curr.y

    # Di chuyển
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:

        nr = r + dr
        nc = c + dc

        if 0 <= nr < self.n and 0 <= nc < self.n:

            child = Node(
                nr,
                nc,
                curr.matrix,
                parent=curr,
                action=f"Đi tới ({nr},{nc})"
            )

            possible_moves.append(child)

    # Hút rác
    if curr.matrix[r][c] == 1:

        new_mat = [row[:] for row in curr.matrix]
        new_mat[r][c] = 0

        child = Node(
            r,
            c,
            new_mat,
            parent=curr,
            action=f"Hút rác tại ({r},{c})"
        )

        possible_moves.append(child)

    return possible_moves


def generate_random_state(self):

    rand_x = random.randint(0, self.n - 1)
    rand_y = random.randint(0, self.n - 1)

    return Node(
        rand_x,
        rand_y,
        self.matrix,
        parent=None,
        action=f"Khởi tạo chùm tại ({rand_x},{rand_y})"
    )


def Local_Beam_Search(self, k=3):

    total_path = []



    current_state_set = []

    start_node = Node(
        self.agent_x,
        self.agent_y,
        self.matrix,
        parent=None,
        action=f"Bắt đầu tại ({self.agent_x},{self.agent_y})"
    )

    current_state_set.append(start_node)
    total_path.append(start_node)

    for _ in range(k - 1):

        rand_node = generate_random_state(self)

        current_state_set.append(rand_node)
        total_path.append(rand_node)

    # Tránh lặp vô hạn
    max_loops = 500
    loops = 0

    visited = set()



    while loops < max_loops:

        loops += 1

        neighbor_states = []

     

        for state in current_state_set:

            neighbors = get_vacuum_neighbors(self, state)

            for neighbor in neighbors:

                state_key = (
                    neighbor.x,
                    neighbor.y,
                    tuple(tuple(row) for row in neighbor.matrix)
                )

                if state_key not in visited:

                    visited.add(state_key)

                    neighbor.parent = state

                    neighbor_states.append(neighbor)

        if not neighbor_states:

            print("Không còn trạng thái để mở rộng.")
            return total_path


        for neighbor in neighbor_states:

            if get_heuristic(self, neighbor) == 0:

                total_path.append(neighbor)

                print("Đã tìm thấy Goal.")

                return total_path

        
        neighbor_states.sort(
            key=lambda node: get_heuristic(self, node)
        )

        current_state_set = neighbor_states[:k]

        for node in current_state_set:
            total_path.append(node)

    print("Đạt giới hạn vòng lặp.")

    return total_path