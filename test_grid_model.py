"""
Unit tests for grid model: grid subdivision and numpad mapping.
"""
import unittest
from grid_model import GridModel, Region


class TestRegion(unittest.TestCase):
    """Test Region class."""
    
    def test_center(self):
        """Test center calculation."""
        region = Region(10, 20, 100, 200)
        center_x, center_y = region.center()
        self.assertEqual(center_x, 60)
        self.assertEqual(center_y, 120)
    
    def test_subdivide(self):
        """Test region subdivision."""
        region = Region(0, 0, 300, 300)
        
        # Top-left (7)
        sub = region.subdivide(0, 0)
        self.assertEqual(sub.x, 0)
        self.assertEqual(sub.y, 0)
        self.assertEqual(sub.width, 100)
        self.assertEqual(sub.height, 100)
        
        # Center (5)
        sub = region.subdivide(1, 1)
        self.assertEqual(sub.x, 100)
        self.assertEqual(sub.y, 100)
        self.assertEqual(sub.width, 100)
        self.assertEqual(sub.height, 100)
        
        # Bottom-right (3)
        sub = region.subdivide(2, 2)
        self.assertEqual(sub.x, 200)
        self.assertEqual(sub.y, 200)
        self.assertEqual(sub.width, 100)
        self.assertEqual(sub.height, 100)
    
    def test_subdivide_with_remainder(self):
        """Test subdivision with non-divisible dimensions."""
        region = Region(0, 0, 100, 100)
        
        # Last column should get remainder
        sub = region.subdivide(0, 2)
        self.assertEqual(sub.width, 34)  # 100 // 3 = 33, remainder 1, so last gets 34
        
        # Last row should get remainder
        sub = region.subdivide(2, 0)
        self.assertEqual(sub.height, 34)


class TestGridModel(unittest.TestCase):
    """Test GridModel class."""
    
    def test_numpad_mapping(self):
        """Test numpad to grid position mapping."""
        # Verify all mappings
        expected = {
            1: (2, 0),  # bottom-left
            2: (2, 1),  # bottom-center
            3: (2, 2),  # bottom-right
            4: (1, 0),  # middle-left
            5: (1, 1),  # middle-center
            6: (1, 2),  # middle-right
            7: (0, 0),  # top-left
            8: (0, 1),  # top-center
            9: (0, 2),  # top-right
        }
        
        for numpad, expected_pos in expected.items():
            self.assertEqual(GridModel.NUMPAD_MAP[numpad], expected_pos)
    
    def test_initialization(self):
        """Test grid model initialization."""
        region = Region(0, 0, 1920, 1080)
        model = GridModel(region)
        
        self.assertEqual(model.get_depth(), 0)
        self.assertEqual(model.get_current_region(), region)
    
    def test_select_region(self):
        """Test region selection."""
        region = Region(0, 0, 900, 900)
        model = GridModel(region)
        
        # Select top-left (7)
        new_region = model.select_region(7)
        self.assertIsNotNone(new_region)
        self.assertEqual(model.get_depth(), 1)
        self.assertEqual(new_region.x, 0)
        self.assertEqual(new_region.y, 0)
        self.assertEqual(new_region.width, 300)
        self.assertEqual(new_region.height, 300)
        
        # Select center (5) of the new region
        new_region2 = model.select_region(5)
        self.assertIsNotNone(new_region2)
        self.assertEqual(model.get_depth(), 2)
        # Should be center of the 300x300 region
        self.assertEqual(new_region2.x, 100)
        self.assertEqual(new_region2.y, 100)
        self.assertEqual(new_region2.width, 100)
        self.assertEqual(new_region2.height, 100)
    
    def test_go_up(self):
        """Test going up one level."""
        region = Region(0, 0, 900, 900)
        model = GridModel(region)
        
        model.select_region(5)
        model.select_region(5)
        self.assertEqual(model.get_depth(), 2)
        
        up_region = model.go_up()
        self.assertIsNotNone(up_region)
        self.assertEqual(model.get_depth(), 1)
        
        # Can't go up from root
        up_region = model.go_up()
        self.assertIsNotNone(up_region)
        self.assertEqual(model.get_depth(), 0)
        
        up_region = model.go_up()
        self.assertIsNone(up_region)
        self.assertEqual(model.get_depth(), 0)
    
    def test_max_depth(self):
        """Test depth limit."""
        region = Region(0, 0, 900, 900)
        model = GridModel(region, max_depth=2)
        
        model.select_region(5)
        self.assertEqual(model.get_depth(), 1)
        
        model.select_region(5)
        self.assertEqual(model.get_depth(), 2)
        
        # Should fail at max depth
        result = model.select_region(5)
        self.assertIsNone(result)
        self.assertEqual(model.get_depth(), 2)
    
    def test_reset(self):
        """Test resetting grid model."""
        region = Region(0, 0, 900, 900)
        model = GridModel(region)
        
        model.select_region(5)
        model.select_region(5)
        self.assertEqual(model.get_depth(), 2)
        
        new_region = Region(100, 100, 800, 800)
        model.reset(new_region)
        
        self.assertEqual(model.get_depth(), 0)
        self.assertEqual(model.get_current_region(), new_region)
    
    def test_get_all_regions(self):
        """Test getting all regions for visualization."""
        region = Region(0, 0, 900, 900)
        model = GridModel(region)
        
        regions = model.get_all_regions()
        self.assertEqual(len(regions), 9)
        
        # Verify first region (top-left, numpad 7)
        self.assertEqual(regions[0].x, 0)
        self.assertEqual(regions[0].y, 0)
        
        # Verify center region (numpad 5)
        self.assertEqual(regions[4].x, 300)
        self.assertEqual(regions[4].y, 300)
        
        # Verify last region (bottom-right, numpad 3)
        self.assertEqual(regions[8].x, 600)
        self.assertEqual(regions[8].y, 600)


if __name__ == '__main__':
    unittest.main()
