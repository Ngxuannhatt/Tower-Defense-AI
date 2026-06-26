import math

class MapManager:
    """
    Manages the 2D grid for the Tower Defense simulation.
    Tracks start/goal nodes, tower types and locations, and provides helpers for pathfinding queries.
    """
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        
        # Default start and goal nodes
        self.start = (0, 0)
        self.goal = (width - 1, height - 1)
        
        # Dictionary mapping tower position (x, y) -> tower_type ("Basic", "Ice", "Fire")
        self.towers = {}

    def is_valid_coord(self, x, y):
        """Checks if the coordinate is within grid boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height

    def add_tower(self, x, y, tower_type="Basic"):
        """
        Adds a tower at (x, y) with a specific type. Towers act as obstacles.
        Cannot add a tower on the start or goal node.
        Returns True if the tower was successfully added, False otherwise.
        """
        if not self.is_valid_coord(x, y):
            return False
        if (x, y) == self.start or (x, y) == self.goal:
            return False
        
        # Normalise tower type string
        if "Ice" in tower_type:
            t_type = "Ice"
        elif "Fire" in tower_type:
            t_type = "Fire"
        else:
            t_type = "Basic"
            
        self.towers[(x, y)] = t_type
        return True

    def remove_tower(self, x, y):
        """
        Removes a tower at (x, y) if present.
        Returns True if a tower was removed, False otherwise.
        """
        if (x, y) in self.towers:
            del self.towers[(x, y)]
            return True
        return False

    def is_obstacle(self, x, y):
        """Checks if a cell is occupied by a tower or is out of bounds."""
        if not self.is_valid_coord(x, y):
            return True
        return (x, y) in self.towers

    def get_neighbors(self, x, y):
        """
        Returns walkable 4-directional neighbors of (x, y).
        Filters out out-of-bounds nodes and obstacles.
        """
        neighbors = []
        # 4 directions: Up, Down, Left, Right
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_coord(nx, ny) and not self.is_obstacle(nx, ny):
                neighbors.append((nx, ny))
                
        return neighbors

    def reset(self):
        """Clears all towers from the grid."""
        self.towers.clear()

    def get_tower_at(self, x, y):
        """Returns the type of tower at (x, y), or None if no tower exists."""
        return self.towers.get((x, y))

    def get_expected_damage(self, x, y):
        """
        Calculates the expected damage of cell (x, y) based on towers in range.
        - Basic: range 3.0, expected damage 10
        - Fire: range 4.0, expected damage 18 (10 * 0.6 + 30 * 0.4)
        - Ice: range 2.0, expected damage 9.5 (5 * 0.7 + 20 * 0.3)
        """
        expected_damage = 0.0
        for (tx, ty), t_type in self.towers.items():
            dist = math.sqrt((tx - x)**2 + (ty - y)**2)
            if t_type == "Basic" and dist <= 3.0:
                expected_damage += 10.0
            elif t_type == "Fire" and dist <= 4.0:
                expected_damage += 18.0
            elif t_type == "Ice" and dist <= 2.0:
                expected_damage += 9.5
        return expected_damage

    def get_freeze_probability(self, x, y):
        """
        Calculates the probability of being frozen at cell (x, y).
        If at least one Ice tower has (x, y) in range (dist <= 2.0),
        probability is 0.3.
        """
        for (tx, ty), t_type in self.towers.items():
            if t_type == "Ice":
                dist = math.sqrt((tx - x)**2 + (ty - y)**2)
                if dist <= 2.0:
                    return 0.3
        return 0.0

