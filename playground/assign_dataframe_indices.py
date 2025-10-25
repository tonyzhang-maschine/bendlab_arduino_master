#!/usr/bin/env python3
"""
Data Frame Index Assignment Tool

Maps sensor_id to data_frame_index based on:
1. Physical coordinates (x_mm, y_mm)
2. Region classification (tip/body/palm)
3. Documentation layout (row-by-row, left-to-right)

Data frame indices are byte positions in the 272-byte frame (0-271)
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Data frame indices from documentation
DATA_FRAME_INDICES = {
    # Finger bodies - ALL sensors in same body share ONE index
    'little_body': 222,
    'ring_body': 219,
    'middle_body': 216,
    'index_body': 213,
    'thumb_body': 210,
    
    # Finger tips - 12 sensors each, 4 rows × 3 columns (row-major order: left→right, top→bottom)
    'little_tip': [
        31, 30, 29,      # Row 1 (top)
        15, 14, 13,      # Row 2
        255, 254, 253,   # Row 3
        239, 238, 237    # Row 4 (bottom)
    ],
    'ring_tip': [
        28, 27, 26,
        12, 11, 10,
        252, 251, 250,
        236, 235, 234
    ],
    'middle_tip': [
        25, 24, 23,
        9, 8, 7,
        249, 248, 247,
        233, 232, 231
    ],
    'index_tip': [
        22, 21, 20,
        6, 5, 4,
        246, 245, 244,
        230, 229, 228
    ],
    'thumb_tip': [
        19, 18, 17,
        3, 2, 1,
        243, 242, 241,
        227, 226, 225
    ],
    
    # Palm - Large grid, row-major order
    'palm': [
        # Row 1
        207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196,
        # Row 2
        191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180, 179, 178, 177,
        # Row 3
        175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161,
        # Row 4
        159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145,
        # Row 5
        143, 142, 141, 140, 139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129
    ]
}


def sort_sensors_by_position(sensors_df, sort_order='grid'):
    """
    Sort sensors by position for row-major grid assignment.
    
    Args:
        sensors_df: DataFrame with x_mm, y_mm columns
        sort_order: 'grid' (row-major: top→bottom, left→right)
    
    Returns:
        Sorted DataFrame
    """
    # Row-major order: Sort by Y descending (top to bottom), then X ascending (left to right)
    return sensors_df.sort_values(by=['y_mm', 'x_mm'], ascending=[False, True])


def assign_finger_tip_indices(sensors_df, finger_name, indices_list):
    """
    Assign data frame indices to finger tip sensors.
    
    Strategy:
    1. Sort sensors by Y (descending, top to bottom)
    2. Within similar Y values, sort by X (ascending, left to right)
    3. Assign indices in row-major order
    """
    sorted_sensors = sort_sensors_by_position(sensors_df)
    
    if len(sorted_sensors) != len(indices_list):
        print(f"⚠️  Warning: {finger_name} has {len(sorted_sensors)} sensors but expected {len(indices_list)}")
        print(f"    Will assign as many as possible")
    
    # Assign indices
    assignments = {}
    for idx, (row_idx, row) in enumerate(sorted_sensors.iterrows()):
        if idx < len(indices_list):
            df_index = indices_list[idx]
            assignments[row['sensor_id']] = df_index  # Use sensor_id from row, not DataFrame index
            print(f"  Sensor {row['sensor_id']:3d} ({row['x_mm']:6.2f}, {row['y_mm']:6.2f}) → DF Index {df_index:3d}")
        else:
            print(f"  Sensor {row['sensor_id']:3d} - No index available!")
    
    return assignments


def assign_palm_indices(sensors_df, indices_list):
    """
    Assign data frame indices to palm sensors.
    
    Strategy: Sort by position (row-major) and assign sequentially
    """
    sorted_sensors = sort_sensors_by_position(sensors_df)
    
    print(f"  Palm has {len(sorted_sensors)} sensors, {len(indices_list)} indices available")
    
    assignments = {}
    for idx, (row_idx, row) in enumerate(sorted_sensors.iterrows()):
        if idx < len(indices_list):
            df_index = indices_list[idx]
            assignments[row['sensor_id']] = df_index  # Use sensor_id from row, not DataFrame index
            if idx < 5 or idx >= len(sorted_sensors) - 5:  # Print first and last 5
                print(f"  Sensor {row['sensor_id']:3d} ({row['x_mm']:6.2f}, {row['y_mm']:6.2f}) → DF Index {df_index:3d}")
            elif idx == 5:
                print(f"  ... ({len(sorted_sensors) - 10} more sensors)")
        else:
            print(f"  ⚠️  Sensor {row['sensor_id']:3d} - No index available!")
    
    return assignments


def assign_dataframe_indices(input_csv, output_csv):
    """
    Main function to assign data frame indices to all sensors.
    """
    print("🔢 Data Frame Index Assignment Tool")
    print("=" * 70)
    
    # Load annotated sensor data
    df = pd.read_csv(input_csv)
    print(f"\n📂 Loaded {len(df)} sensors from {input_csv}")
    
    # Check regions
    print(f"\n📊 Regions found:")
    for region, count in df['region'].value_counts().sort_index().items():
        print(f"  {region:20s}: {count:3d} sensors")
    
    # Initialize data_frame_index column
    df['data_frame_index'] = -1  # -1 = unassigned
    
    all_assignments = {}
    
    print("\n" + "=" * 70)
    print("🎯 ASSIGNING DATA FRAME INDICES")
    print("=" * 70)
    
    # Process each region
    for region in sorted(df['region'].unique()):
        print(f"\n📍 {region.upper().replace('_', ' ')}")
        print("-" * 70)
        
        region_sensors = df[df['region'] == region]
        
        if region.endswith('_body'):
            # Finger body - all sensors share one index
            shared_index = DATA_FRAME_INDICES[region]
            print(f"  All {len(region_sensors)} sensors → Shared DF Index {shared_index}")
            
            for sensor_id in region_sensors['sensor_id']:
                all_assignments[sensor_id] = shared_index
        
        elif region.endswith('_tip'):
            # Finger tip - unique indices per sensor
            indices_list = DATA_FRAME_INDICES[region]
            assignments = assign_finger_tip_indices(region_sensors, region, indices_list)
            all_assignments.update(assignments)
        
        elif region == 'palm':
            # Palm - many unique indices
            indices_list = DATA_FRAME_INDICES[region]
            assignments = assign_palm_indices(region_sensors, indices_list)
            all_assignments.update(assignments)
        
        else:
            print(f"  ⚠️  Unknown region type: {region}")
    
    # Apply assignments to dataframe
    df['data_frame_index'] = df['sensor_id'].map(all_assignments)
    
    # Mark unassigned sensors with -1 instead of NaN for clarity
    df['data_frame_index'] = df['data_frame_index'].fillna(-1).astype(int)
    
    # Validation
    print("\n" + "=" * 70)
    print("✅ VALIDATION")
    print("=" * 70)
    
    unassigned = df[df['data_frame_index'] == -1]
    if len(unassigned) > 0:
        print(f"⚠️  {len(unassigned)} sensors UNASSIGNED (marked with -1):")
        print(f"   These sensors exceed available data frame indices in documentation.")
        print(f"   Will require manual filtering/correction later.\n")
        for _, row in unassigned.iterrows():
            print(f"  Sensor {row['sensor_id']:3d}: {row['region']:15s} ({row['x_mm']:6.2f}, {row['y_mm']:6.2f})")
    else:
        print("✓ All sensors assigned!")
    
    # Check for duplicates (except body sensors which should duplicate)
    duplicates = df[~df['region'].str.endswith('_body')].groupby('data_frame_index').size()
    duplicates = duplicates[duplicates > 1]
    if len(duplicates) > 0:
        print(f"\n⚠️  Duplicate indices found (non-body sensors):")
        for idx, count in duplicates.items():
            print(f"  DF Index {idx}: {count} sensors")
            sensors = df[df['data_frame_index'] == idx]
            for _, row in sensors.iterrows():
                print(f"    - Sensor {row['sensor_id']}: {row['region']}")
    else:
        print("✓ No unexpected duplicate indices!")
    
    # Statistics
    assigned = df[df['data_frame_index'] != -1]
    unassigned = df[df['data_frame_index'] == -1]
    
    print(f"\n📊 Statistics:")
    print(f"  Total sensors:        {len(df)}")
    print(f"  Assigned:             {len(assigned)}")
    print(f"  Unassigned:           {len(unassigned)}")
    if len(assigned) > 0:
        print(f"  Unique DF indices:    {assigned['data_frame_index'].nunique()}")
        print(f"  DF index range:       {int(assigned['data_frame_index'].min())} - {int(assigned['data_frame_index'].max())}")
    
    # Save
    print(f"\n💾 Saving to {output_csv}")
    df.to_csv(output_csv, index=False)
    
    print("\n✅ Complete!")
    print(f"\n📋 Output columns: sensor_id, x_mm, y_mm, region, data_frame_index")
    
    return df


def main():
    input_file = Path(__file__).parent / "glove_sensor_map_annotated.csv"
    output_file = Path(__file__).parent / "glove_sensor_map_with_indices.csv"
    
    if not input_file.exists():
        print(f"❌ Error: {input_file} not found!")
        print("   Please ensure you have completed annotation first.")
        return
    
    df = assign_dataframe_indices(input_file, output_file)
    
    print(f"\n🎉 Success! Review {output_file.name} for results.")


if __name__ == '__main__':
    main()

