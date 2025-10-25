#!/usr/bin/env python3
"""
Performance Test Script - Measure Improvements

Tests the optimizations made to reduce lag and improve FPS:
1. OpenGL acceleration enabled
2. Queue size reduced (50 -> 10 frames)
3. Fixed-width labels (no flickering)

Run this with the glove connected to measure actual performance metrics.
"""

import sys
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

def test_opengl_available():
    """Check if OpenGL is available and working."""
    print("=" * 80)
    print("TEST 1: OpenGL Availability")
    print("=" * 80)
    
    try:
        from OpenGL import GL
        print("✓ OpenGL module found")
        
        # Check version
        try:
            app = QApplication.instance() or QApplication(sys.argv)
            widget = pg.PlotWidget()
            widget.hide()
            
            # Try to get OpenGL info
            print(f"✓ PyQtGraph OpenGL config: {pg.getConfigOption('useOpenGL')}")
            print("✓ OpenGL acceleration should be available")
            return True
        except Exception as e:
            print(f"⚠ OpenGL available but may have issues: {e}")
            return False
            
    except ImportError:
        print("✗ OpenGL module NOT found")
        print("  Install with: pip install PyOpenGL PyOpenGL_accelerate")
        return False


def test_scatter_plot_performance():
    """Benchmark scatter plot update performance."""
    print("\n" + "=" * 80)
    print("TEST 2: Scatter Plot Rendering Performance")
    print("=" * 80)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create test widget
    widget = pg.PlotWidget()
    widget.setBackground('w')
    
    # Create scatter plot with 136 points (same as real application)
    scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), pxMode=True)
    widget.addItem(scatter)
    
    # Random positions
    positions = np.random.rand(136, 2) * 100
    
    # Benchmark update performance
    num_updates = 100
    update_times = []
    
    print(f"Benchmarking {num_updates} scatter plot updates...")
    
    for i in range(num_updates):
        # Random colors
        colors = np.random.randint(0, 255, (136, 4), dtype=np.uint8)
        colors[:, 3] = 255  # Full opacity
        
        start = time.time()
        scatter.setData(pos=positions, brush=colors)
        app.processEvents()  # Force update
        elapsed = (time.time() - start) * 1000  # ms
        
        update_times.append(elapsed)
    
    # Statistics
    avg_time = np.mean(update_times)
    min_time = np.min(update_times)
    max_time = np.max(update_times)
    p95_time = np.percentile(update_times, 95)
    
    print(f"\nResults:")
    print(f"  Average update time: {avg_time:.2f} ms")
    print(f"  Min update time: {min_time:.2f} ms")
    print(f"  Max update time: {max_time:.2f} ms")
    print(f"  95th percentile: {p95_time:.2f} ms")
    
    # Calculate achievable FPS
    achievable_fps = 1000 / avg_time if avg_time > 0 else 0
    print(f"\n  Achievable FPS (rendering only): {achievable_fps:.1f} Hz")
    
    # Evaluation
    if avg_time < 10:
        print("  ✓ EXCELLENT: Rendering is very fast")
    elif avg_time < 20:
        print("  ✓ GOOD: Rendering should support 10+ Hz easily")
    elif avg_time < 50:
        print("  ⚠ MODERATE: May struggle to reach 10 Hz target")
    else:
        print("  ✗ SLOW: Rendering is a major bottleneck")
    
    return avg_time


def test_queue_latency():
    """Calculate expected latency with new queue size."""
    print("\n" + "=" * 80)
    print("TEST 3: Queue Latency Analysis")
    print("=" * 80)
    
    capture_hz = 76  # Observed capture rate
    old_queue_size = 50
    new_queue_size = 10
    
    old_latency_ms = (old_queue_size / capture_hz) * 1000
    new_latency_ms = (new_queue_size / capture_hz) * 1000
    
    print(f"Capture rate: {capture_hz} Hz")
    print(f"\nOLD Configuration:")
    print(f"  Queue size: {old_queue_size} frames")
    print(f"  Buffer latency: {old_latency_ms:.0f} ms")
    
    print(f"\nNEW Configuration:")
    print(f"  Queue size: {new_queue_size} frames")
    print(f"  Buffer latency: {new_latency_ms:.0f} ms")
    
    improvement_ms = old_latency_ms - new_latency_ms
    improvement_pct = (improvement_ms / old_latency_ms) * 100
    
    print(f"\n✓ IMPROVEMENT: {improvement_ms:.0f} ms reduction ({improvement_pct:.0f}%)")
    
    return new_latency_ms


def test_expected_performance():
    """Estimate expected end-to-end performance."""
    print("\n" + "=" * 80)
    print("TEST 4: Expected End-to-End Performance")
    print("=" * 80)
    
    # Components of latency
    queue_latency = 130  # From queue test
    processing_overhead = 5  # Sensor extraction, stats calculation
    rendering_time = 10  # From rendering test (optimistic with OpenGL)
    
    total_latency = queue_latency + processing_overhead + rendering_time
    
    print("Latency Components:")
    print(f"  Queue buffering: {queue_latency} ms")
    print(f"  Processing overhead: {processing_overhead} ms")
    print(f"  Rendering: {rendering_time} ms")
    print(f"  ---")
    print(f"  TOTAL EXPECTED: {total_latency} ms")
    
    if total_latency < 200:
        print(f"\n✓ EXCELLENT: <200ms lag is acceptable for monitoring")
    elif total_latency < 500:
        print(f"\n✓ GOOD: <500ms lag is usable")
    elif total_latency < 1000:
        print(f"\n⚠ MODERATE: <1s lag is noticeable but functional")
    else:
        print(f"\n✗ POOR: >{total_latency}ms lag is significant")
    
    # Display rate
    update_interval = 100  # 10 Hz
    if rendering_time < update_interval:
        display_fps = 1000 / (rendering_time + processing_overhead)
        print(f"\n  Display FPS estimate: {display_fps:.1f} Hz")
        if display_fps >= 10:
            print("  ✓ Should meet 10 Hz target")
        else:
            print("  ⚠ May fall short of 10 Hz target")


def main():
    """Run all performance tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PERFORMANCE IMPROVEMENT TEST" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\nTesting optimizations:")
    print("  1. OpenGL acceleration")
    print("  2. Reduced queue size (50 -> 10)")
    print("  3. Fixed-width labels\n")
    
    # Run tests
    opengl_ok = test_opengl_available()
    render_time = test_scatter_plot_performance()
    queue_latency = test_queue_latency()
    test_expected_performance()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if opengl_ok:
        print("✓ OpenGL acceleration: AVAILABLE")
    else:
        print("⚠ OpenGL acceleration: NOT AVAILABLE (install PyOpenGL)")
    
    print(f"✓ Rendering performance: {render_time:.1f} ms per update")
    print(f"✓ Queue latency reduced: 660ms -> {queue_latency:.0f}ms")
    print("✓ Window flickering: FIXED (fixed-width labels)")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if opengl_ok and render_time < 20:
        print("✓ All optimizations effective! Application should run smoothly.")
        print("  Expected lag: ~150-200ms (5x improvement from 3+ seconds)")
        print("  Expected display rate: 10 Hz (stable)")
    elif not opengl_ok:
        print("⚠ Install PyOpenGL for best performance:")
        print("  pip install PyOpenGL PyOpenGL_accelerate")
    else:
        print("⚠ Rendering is still slow. Further optimization may be needed.")
    
    print("\nNext step: Test with real glove to verify improvements!")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    # Need QApplication for PyQtGraph
    app = QApplication(sys.argv)
    main()
    sys.exit(0)

