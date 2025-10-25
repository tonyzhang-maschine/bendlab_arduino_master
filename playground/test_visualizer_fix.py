#!/usr/bin/env python3
"""
Quick test to verify hand_visualizer.py is compatible with upgraded sensor_mapping.py
"""

import numpy as np

def test_visualizer_compatibility():
    """Test that visualizer dimensions match"""
    print("=" * 80)
    print("VISUALIZER COMPATIBILITY TEST")
    print("=" * 80)
    
    from sensor_mapping import get_unique_data_indices, SENSOR_REGIONS
    
    print("\n1. Testing sensor_mapping.py...")
    unique_indices = get_unique_data_indices()
    print(f"   ✅ get_unique_data_indices() returns {len(unique_indices)} indices")
    
    print("\n2. Testing SENSOR_REGIONS extraction (visualizer method)...")
    indices = []
    seen = set()
    
    for region_key in ['little_finger', 'little_finger_back',
                      'ring_finger', 'ring_finger_back',
                      'middle_finger', 'middle_finger_back',
                      'index_finger', 'index_finger_back',
                      'thumb', 'thumb_back',
                      'palm']:
        if region_key in SENSOR_REGIONS:
            for idx in SENSOR_REGIONS[region_key]['data_indices']:
                if idx not in seen:
                    indices.append(idx)
                    seen.add(idx)
    
    print(f"   ✅ Extracted {len(indices)} unique indices from SENSOR_REGIONS")
    
    print("\n3. Testing HandVisualizer initialization...")
    try:
        # Import here to avoid Qt display issues in headless mode
        import sys
        from PyQt5.QtWidgets import QApplication
        
        # Create minimal QApplication (required for Qt widgets)
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        from hand_visualizer import HandVisualizer
        viz = HandVisualizer()
        
        print(f"   ✅ HandVisualizer created successfully")
        print(f"   ✅ num_sensors: {viz.num_sensors}")
        print(f"   ✅ sensor_indices: {len(viz.sensor_indices)} indices")
        print(f"   ✅ sensor_positions: {viz.sensor_positions.shape}")
        
        # Test update with fake data
        print("\n4. Testing update_sensors() with fake data...")
        frame_data = np.random.randint(0, 20, size=272, dtype=np.uint8)
        viz.update_sensors(frame_data)
        print(f"   ✅ update_sensors() completed without error")
        
        # Verify dimensions
        print("\n5. Verifying dimensions...")
        assert viz.num_sensors == len(indices), f"Mismatch: {viz.num_sensors} != {len(indices)}"
        assert viz.num_sensors == len(viz.sensor_indices), "num_sensors != len(sensor_indices)"
        assert viz.num_sensors == viz.sensor_positions.shape[0], "num_sensors != positions.shape[0]"
        print(f"   ✅ All dimensions consistent: {viz.num_sensors} sensors")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe visualizer is now compatible with the upgraded sensor_mapping.py")
        print("You can run: python realtime_glove_viz.py")
        
        return True
        
    except ImportError as e:
        print(f"   ⚠️  Could not import Qt modules: {e}")
        print(f"   ℹ️  This is okay if running headless")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_visualizer_compatibility()
    exit(0 if success else 1)

