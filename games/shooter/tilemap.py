"""
Tilemap system for procedural level generation
"""


class Tilemap:
    def __init__(self, tile_size=40):
        self.tile_size = tile_size
        self.tiles = {}  # {(x, y): {"neighbor_count": int, "corner": True/False}}
    
    def place_tile(self, gx, gy, update=True):
        """Place a tile at grid position"""
        self.tiles[(gx, gy)] = {"neighbor_count": 0, "corner": False}
        if update:
            self.update_tiles()
    
    def remove_tile(self, gx, gy, update=True):
        """Remove a tile at grid position"""
        if (gx, gy) in self.tiles:
            del self.tiles[(gx, gy)]
            if update:
                self.update_tiles()
    
    def has_tile(self, gx, gy):
        """Check if tile exists at grid position"""
        return (gx, gy) in self.tiles
    
    def update_tiles(self):
        """Update neighbor counts and corner flags for all tiles"""
        new_tiles = {}
        for (gx, gy) in self.tiles:
            # Cardinal neighbors
            n_up = (gx, gy - 1) in self.tiles
            n_down = (gx, gy + 1) in self.tiles
            n_left = (gx - 1, gy) in self.tiles
            n_right = (gx + 1, gy) in self.tiles
            
            # Count cardinal neighbors
            neighbor_count = sum([n_up, n_down, n_left, n_right])
            
            # Diagonal neighbors
            d_tl = (gx - 1, gy - 1) in self.tiles
            d_tr = (gx + 1, gy - 1) in self.tiles
            d_bl = (gx - 1, gy + 1) in self.tiles
            d_br = (gx + 1, gy + 1) in self.tiles
            
            # Corner flag: True only if missing diagonal neighbor
            corner = not (d_tl and d_tr and d_bl and d_br)
            
            new_tiles[(gx, gy)] = {"neighbor_count": neighbor_count, "corner": corner}
        
        self.tiles = new_tiles
    
    def get_all_tiles(self):
        """Get all tile positions"""
        return list(self.tiles.keys())
    
    def check_collision(self, x, y, size):
        """Check if a point collides with any tile (works even if walls not rendered)"""
        # Convert world position to grid position
        gx = int(x // self.tile_size)
        gy = int(y // self.tile_size)
        
        # Check the tile and adjacent tiles for collision
        for check_gx in range(gx - 1, gx + 2):
            for check_gy in range(gy - 1, gy + 2):
                if (check_gx, check_gy) in self.tiles:
                    # Calculate tile world bounds
                    tile_x = check_gx * self.tile_size
                    tile_y = check_gy * self.tile_size
                    
                    # Simple AABB collision
                    if (x + size > tile_x and x - size < tile_x + self.tile_size and
                        y + size > tile_y and y - size < tile_y + self.tile_size):
                        return True
        
        return False
