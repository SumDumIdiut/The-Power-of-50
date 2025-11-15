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
