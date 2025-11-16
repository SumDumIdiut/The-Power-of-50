"""
Wall rendering system with tile-based colors
"""
import pygame


class WallRenderer:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        # Pre-create color surfaces for batch rendering
        self.tile_size = tilemap.tile_size
        self.color_surfaces = {}
        self._create_color_surfaces()
        
        # Track loaded tile regions for gradual unloading
        self.loaded_tile_regions = {}  # {(chunk_x, chunk_y): frame_last_visible}
        self.tile_chunk_size = 10  # Group tiles into 10x10 chunks for unloading
        self.unload_delay = 180  # Frames before unloading (3 seconds at 60fps)

    def _create_color_surfaces(self):
        """Pre-create surfaces for each color to speed up rendering"""
        colors = {
            4: (100, 200, 100),  # Green for 4 neighbors
            3: (200, 100, 100),  # Red for 3 neighbors
            2: (100, 100, 200),  # Blue for 2 neighbors
            1: (150, 150, 150),  # Gray for 0-1 neighbors
            0: (150, 150, 150),
        }
        
        for neighbor_count, color in colors.items():
            surf = pygame.Surface((self.tile_size, self.tile_size))
            surf.fill(color)
            self.color_surfaces[neighbor_count] = surf

    def draw_tiles(self, screen, camera_x, camera_y, screen_width, screen_height, current_frame=0):
        """Draw visible tiles with colors based on neighbor count (with gradual unloading)"""
        tile_size = self.tile_size
        
        # Calculate visible tile range with small buffer
        start_x = max(0, int(camera_x // tile_size) - 1)
        start_y = max(0, int(camera_y // tile_size) - 1)
        end_x = int((camera_x + screen_width) // tile_size) + 2
        end_y = int((camera_y + screen_height) // tile_size) + 2
        
        # Track which tile chunks are visible this frame
        visible_chunks = set()
        
        # Batch tiles by color for more efficient rendering
        tiles_by_color = {0: [], 1: [], 2: [], 3: [], 4: []}
        
        # Collect visible tiles and mark chunks as visible
        for gx in range(start_x, end_x):
            for gy in range(start_y, end_y):
                # Mark this tile chunk as visible
                chunk_x = gx // self.tile_chunk_size
                chunk_y = gy // self.tile_chunk_size
                chunk_key = (chunk_x, chunk_y)
                visible_chunks.add(chunk_key)
                self.loaded_tile_regions[chunk_key] = current_frame
                
                if (gx, gy) in self.tilemap.tiles:
                    tile_info = self.tilemap.tiles[(gx, gy)]
                    neighbor_count = tile_info["neighbor_count"]
                    
                    # Calculate screen position (use integers to align with grid)
                    screen_x = int(gx * tile_size - camera_x)
                    screen_y = int(gy * tile_size - camera_y)
                    
                    tiles_by_color[neighbor_count].append((screen_x, screen_y))
        
        # Draw tiles in batches by color
        for neighbor_count, positions in tiles_by_color.items():
            if positions and neighbor_count in self.color_surfaces:
                surf = self.color_surfaces[neighbor_count]
                for screen_x, screen_y in positions:
                    screen.blit(surf, (screen_x, screen_y))
        
        # Gradually unload distant tile regions (visual only, collision stays)
        chunks_to_unload = []
        for chunk_key, last_frame in list(self.loaded_tile_regions.items()):
            if current_frame - last_frame > self.unload_delay:
                chunks_to_unload.append(chunk_key)
        
        # Unload old chunks (just remove from tracking, tiles stay in tilemap for collision)
        for chunk_key in chunks_to_unload:
            del self.loaded_tile_regions[chunk_key]

    def find_adjacent_walls(self, wall, all_walls):
        """Find walls adjacent to this wall (kept for compatibility)"""
        return {"top": [], "bottom": [], "left": [], "right": []}

    def draw_wall(self, screen, wall, camera_x, camera_y, adjacent_walls):
        """Draw a single wall (kept for compatibility but not used)"""
        pass
