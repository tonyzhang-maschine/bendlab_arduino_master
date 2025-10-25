#!/usr/bin/env python3
"""
Colormap Comparison Demo

Shows a visual comparison of all available colormaps
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def create_colormaps():
    """Create all colormaps matching hand_visualizer.py implementations"""
    
    # Viridis
    viridis_colors = [
        (68/255, 1/255, 84/255),      # Dark purple
        (59/255, 82/255, 139/255),    # Purple
        (33/255, 144/255, 140/255),   # Teal
        (94/255, 201/255, 98/255),    # Green
        (253/255, 231/255, 37/255),   # Yellow
    ]
    viridis = LinearSegmentedColormap.from_list('viridis', viridis_colors)
    
    # Plasma
    plasma_colors = [
        (13/255, 8/255, 135/255),      # Dark purple
        (126/255, 3/255, 168/255),     # Purple
        (204/255, 71/255, 120/255),    # Magenta
        (240/255, 142/255, 53/255),    # Orange
        (240/255, 249/255, 33/255),    # Yellow
    ]
    plasma = LinearSegmentedColormap.from_list('plasma', plasma_colors)
    
    # Turbo
    turbo_colors = [
        (48/255, 18/255, 59/255),      # Blue
        (34/255, 167/255, 227/255),    # Cyan
        (31/255, 228/255, 139/255),    # Green
        (189/255, 230/255, 43/255),    # Yellow
        (249/255, 152/255, 40/255),    # Orange
        (122/255, 4/255, 3/255),       # Red
    ]
    turbo = LinearSegmentedColormap.from_list('turbo', turbo_colors)
    
    # YlOrRd (Yellow-Orange-Red)
    ylorrd_colors = [
        (255/255, 255/255, 178/255),   # Bright yellow
        (255/255, 178/255, 0),         # Orange
        (128/255, 0, 0),               # Dark red
    ]
    ylorrd = LinearSegmentedColormap.from_list('YlOrRd', ylorrd_colors)
    
    # Hot (original)
    hot_colors = [
        (0, 0, 0),                      # Black
        (128/255, 0, 0),                # Dark red
        (255/255, 128/255, 0),          # Orange
        (255/255, 255/255, 0),          # Yellow
    ]
    hot = LinearSegmentedColormap.from_list('hot', hot_colors)
    
    return {
        'viridis': viridis,
        'plasma': plasma,
        'turbo': turbo,
        'YlOrRd': ylorrd,
        'hot': hot
    }

def main():
    """Create colormap comparison figure"""
    colormaps = create_colormaps()
    
    # Create sample data (gradient from 0 to 1)
    gradient = np.linspace(0, 1, 256).reshape(1, 256)
    
    # Create figure
    fig, axes = plt.subplots(len(colormaps), 1, figsize=(10, 6))
    fig.suptitle('Colormap Comparison - JQ Glove Visualization', fontsize=14, fontweight='bold')
    
    descriptions = {
        'viridis': 'Purple → Blue → Green → Yellow (Recommended: Perceptually uniform, colorblind-friendly)',
        'plasma': 'Purple → Pink → Orange → Yellow (High contrast, vibrant)',
        'turbo': 'Blue → Cyan → Green → Yellow → Red (Very visible, full spectrum)',
        'YlOrRd': 'Yellow → Orange → Red (Bright, great for seeing low values)',
        'hot': 'Black → Red → Orange → Yellow (Original, dark at low values)'
    }
    
    for idx, (name, cmap) in enumerate(colormaps.items()):
        ax = axes[idx]
        ax.imshow(gradient, aspect='auto', cmap=cmap)
        ax.set_yticks([])
        ax.set_xticks([0, 64, 128, 192, 255])
        ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
        ax.set_ylabel(name.capitalize(), fontsize=11, fontweight='bold')
        ax.set_title(descriptions[name], fontsize=9, loc='left', pad=2)
    
    plt.xlabel('Pressure Value', fontsize=11)
    plt.tight_layout()
    
    print("\n" + "="*70)
    print("COLORMAP COMPARISON - JQ Glove Visualization")
    print("="*70)
    print("\n✨ Available Colormaps:\n")
    
    for name, desc in descriptions.items():
        print(f"  • {name.upper()}:")
        print(f"    {desc}")
        print()
    
    print("="*70)
    print("\n💡 RECOMMENDATIONS:\n")
    print("  1. VIRIDIS (Default) - Best overall choice")
    print("     ✓ Easy to see low and high values")
    print("     ✓ Perceptually uniform (equal steps look equal)")
    print("     ✓ Colorblind-friendly")
    print()
    print("  2. YLORRD - If you want maximum brightness")
    print("     ✓ Starts with bright yellow (very visible)")
    print("     ✓ Great for seeing subtle pressure changes")
    print()
    print("  3. TURBO - If you want full rainbow")
    print("     ✓ Covers full visible spectrum")
    print("     ✓ Very colorful and distinctive")
    print()
    print("  4. PLASMA - High contrast alternative to viridis")
    print("     ✓ More vibrant than viridis")
    print("     ✓ Still perceptually uniform")
    print()
    print("  5. HOT - Original (not recommended)")
    print("     ✗ Too dark at low values")
    print("     ✗ Hard to see subtle differences")
    print()
    print("="*70)
    print("\nShowing comparison plot...")
    print("Close the plot window to exit.\n")
    
    plt.show()

if __name__ == '__main__':
    main()

