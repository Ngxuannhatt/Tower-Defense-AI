class MapManager:
    """
    Manages the 2D grid for the Tower Defense simulation.
    Tracks start/goal nodes, tower locations, and provides helpers for pathfinding queries.
    """
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        
        # Default start and goal nodes
        self.start = (0, 0)
        self.goal = (width - 1, height - 1)
        
        # Set of tower positions: set of (x, y) tuples
        self.towers = set()

    def is_valid_coord(self, x, y):
        """Checks if the coordinate is within grid boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height

    def add_tower(self, x, y):
        """
        Adds a tower at (x, y). Towers act as obstacles.
        Cannot add a tower on the start or goal node.
        Returns True if the tower was successfully added, False otherwise.
        """
        if not self.is_valid_coord(x, y):
            return False
        if (x, y) == self.start or (x, y) == self.goal:
            return False
        
        self.towers.add((x, y))
        return True

    def remove_tower(self, x, y):
        """
        Removes a tower at (x, y) if present.
        Returns True if a tower was removed, False otherwise.
        """
        if (x, y) in self.towers:
            self.towers.remove((x, y))
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
