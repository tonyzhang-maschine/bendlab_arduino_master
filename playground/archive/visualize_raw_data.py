#!/usr/bin/env python3
"""
Visualize raw data indices to see where actual pressure values are
"""

import sys
import matplotlib.pyplot as plt
import numpy as np

# Read binary file
filename = sys.argv[1] if len(sys.argv) > 1 else "glove_data_20251024_214706.bin"

with open(filename, 'rb') as f:
    data = f.read()

# Find and parse packets
DELIM = bytes([0xAA, 0x55, 0x03, 0x99])
packets = []
start = 0

while True:
    pos = data.find(DELIM, start)
    if pos == -1:
        break
    
    if start > 0:
        packet = data[start:pos]
        if len(packet) > 2:
            packets.append({
                'index': packet[0],
                'type': packet[1],
                'data': packet[2:]
            })
    
    start = pos + 4

print(f"Found {len(packets)} packets")

# Combine first frame (packet 0x02 + 0x01)
frame_data = None
for i in range(len(packets) - 1):
    if packets[i]['index'] == 0x02 and packets[i+1]['index'] == 0x01:
        # Combine: packet 0x01 first, then 0x02
        data1 = [int(b) for b in packets[i+1]['data']]
        data2 = [int(b) for b in packets[i]['data']]
        frame_data = data1 + data2
        break

if frame_data is None:
    print("Could not find frame pair!")
    sys.exit(1)

print(f"Frame data: {len(frame_data)} bytes")

# Create visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

# Plot 1: All values as heatmap
ax1.imshow([frame_data], aspect='auto', cmap='hot', interpolation='nearest')
ax1.set_title(f'Raw Frame Data - All {len(frame_data)} bytes', fontsize=14, fontweight='bold')
ax1.set_xlabel('Byte Index')
ax1.set_yticks([])
ax1.set_xlim(-0.5, len(frame_data)-0.5)

# Add colorbar
cbar1 = plt.colorbar(ax1.images[0], ax=ax1, orientation='horizontal', pad=0.1)
cbar1.set_label('Value (ADC Reading)', fontsize=12)

# Plot 2: Bar chart of non-zero values
non_zero_indices = [i for i, v in enumerate(frame_data) if v > 0]
non_zero_values = [frame_data[i] for i in non_zero_indices]

colors = plt.cm.hot(np.array(non_zero_values) / max(non_zero_values))
ax2.bar(non_zero_indices, non_zero_values, color=colors, width=1.0)
ax2.set_title(f'Non-Zero Values Only ({len(non_zero_indices)} active bytes)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Byte Index in Frame', fontsize=12)
ax2.set_ylabel('Value (ADC Reading)', fontsize=12)
ax2.grid(True, alpha=0.3)

# Annotate clusters
if non_zero_indices:
    for idx, val in zip(non_zero_indices[:15], non_zero_values[:15]):
        ax2.text(idx, val + 5, str(idx), ha='center', va='bottom', fontsize=8, rotation=90)

plt.tight_layout()

output_file = f"{filename.replace('.bin', '')}_raw_visualization.png"
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"\n✓ Saved to: {output_file}")

plt.show()

# Print summary
print(f"\n📊 Summary:")
print(f"  Total bytes: {len(frame_data)}")
print(f"  Non-zero bytes: {len(non_zero_indices)}")
print(f"  Value range: {min(frame_data)} - {max(frame_data)}")
print(f"\n  Non-zero index clusters:")

# Find clusters
if non_zero_indices:
    cluster_start = non_zero_indices[0]
    cluster_end = non_zero_indices[0]
    
    for i in range(1, len(non_zero_indices)):
        if non_zero_indices[i] - non_zero_indices[i-1] <= 5:  # Within 5 indices
            cluster_end = non_zero_indices[i]
        else:
            print(f"    Indices {cluster_start}-{cluster_end}")
            cluster_start = non_zero_indices[i]
            cluster_end = non_zero_indices[i]
    
    print(f"    Indices {cluster_start}-{cluster_end}")

