#!/usr/bin/env python3
"""
Test script to demonstrate the off-by-one indexing problem.

This script shows:
1. Current (incorrect) mapping: df_index directly as array index
2. Proposed (correct) mapping: df_index - 1 as array index
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("OFF-BY-ONE INDEXING TEST")
print("=" * 80)

# Load the CSV
df = pd.read_csv('glove_sensor_map_annotated_w_dataframe_indices.csv')

# Create a test frame where byte value = byte position
# This makes it easy to see which byte we're reading
test_frame = np.arange(272, dtype=np.uint8)  # [0, 1, 2, ..., 271]

print("\nTest Frame Setup:")
print("  Frame[i] = i for all positions")
print(f"  Frame[0] = {test_frame[0]}")
print(f"  Frame[1] = {test_frame[1]}")
print(f"  Frame[23] = {test_frame[23]}")
print()

# Get a few example sensors
examples = df[df['sensor_id'].isin([1, 2, 4, 75])].copy()

print("Example Sensor Mappings:")
print("-" * 80)
print(f"{'Sensor ID':<12} {'Region':<15} {'df_index':<10} {'Current':<12} {'Proposed':<12} {'Diff':<8}")
print("-" * 80)

for _, sensor in examples.iterrows():
    sensor_id = int(sensor['sensor_id'])
    region = sensor['region']
    df_index = int(sensor['data_frame_index'])

    # Current approach (possibly wrong)
    current_value = test_frame[df_index] if df_index < len(test_frame) else -1

    # Proposed approach (correct)
    proposed_value = test_frame[df_index - 1] if df_index > 0 else -1

    diff = "SAME" if current_value == proposed_value else "DIFFERENT"

    print(f"{sensor_id:<12} {region:<15} {df_index:<10} "
          f"[{df_index}]={current_value:<7} [{df_index-1}]={proposed_value:<7} {diff:<8}")

print()
print("=" * 80)
print("KEY OBSERVATION:")
print("=" * 80)
print()
print("With test frame where frame[i] = i:")
print("  - Current code reads: frame[df_index] → returns the df_index value")
print("  - Proposed code reads: frame[df_index - 1] → returns (df_index - 1) value")
print()
print("If df_index represents a 1-BASED position (as documentation suggests):")
print("  - df_index=1 means 'first sensor byte' → should read frame[0]")
print("  - df_index=23 means '23rd sensor byte' → should read frame[22]")
print()
print("Evidence for 1-based indexing:")
print("  ✓ Minimum df_index in CSV: 1 (not 0)")
print("  ✓ Maximum df_index in CSV: 255 (suggests first 256 bytes are 1-based)")
print("  ✓ Index 0 is NEVER used in any sensor mapping")
print("  ✓ Strange sensor patterns observed in testing (off-by-one symptoms)")
print()

# Check index coverage
valid_indices = df[df['data_frame_index'] != -1]['data_frame_index'].values
print("Index Statistics:")
print(f"  Used indices: {len(valid_indices)} sensors map to {len(set(valid_indices))} unique indices")
print(f"  Range: {min(valid_indices)} to {max(valid_indices)}")
print(f"  Index 0 used: {0 in valid_indices}")
print(f"  Indices 256-271 used: {any(i >= 256 for i in valid_indices)}")
print()

# Show what data would be in position 0
print("What's at position 0?")
print(f"  Frame[0] = {test_frame[0]}")
print("  No sensor is mapped to read this position!")
print("  This byte is either:")
print("    a) Unused/reserved")
print("    b) Header/metadata")
print("    c) Evidence that indexing is 1-based (most likely!)")
print()

print("=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print()
print("Change all code from:")
print("    sensor_value = frame_data[df_index]")
print()
print("To:")
print("    sensor_value = frame_data[df_index - 1]  # Convert 1-based to 0-based")
print()
print("=" * 80)
