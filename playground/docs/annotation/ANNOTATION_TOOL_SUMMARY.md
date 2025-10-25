# Sensor Annotation Tool - Summary

## What Was Created

### 1. Interactive Annotation Tool (`annotate_sensors.py`)
A PyQt5-based GUI application for visually labeling sensor regions.

**Features:**
- ✅ Load CSV with sensor coordinates
- ✅ Multiple selection modes (Rectangle, Lasso, Click)
- ✅ 6 region buttons (Thumb, Index, Middle, Ring, Little, Palm)
- ✅ Real-time visualization with color coding
- ✅ Statistics panel showing sensor counts
- ✅ Undo functionality
- ✅ Save annotated CSV with region column

### 2. Documentation
- **`ANNOTATION_GUIDE.md`** - Complete usage instructions
- Updated **`README.md`** - Added annotation tool section
- **`run_annotation_tool.sh`** - Quick launch script

### 3. Dependencies
- Added `pandas>=2.0.0` to requirements.txt
- Installed using `uv pip install`

---

## How to Use

### Quick Start
```bash
cd playground
./run_annotation_tool.sh
```

Or manually:
```bash
cd playground
../.venv/bin/python annotate_sensors.py
```

### Workflow
1. **Launch tool** → Click "Load CSV" → Select `glove_sensor_map_refined.csv`
2. **Select sensors** using Rectangle/Lasso/Click mode
3. **Assign to region** by clicking region button
4. **Repeat** for all regions
5. **Save** as `glove_sensor_map_annotated.csv`

---

## Selection Modes

### Rectangle (Recommended for large areas)
- Click → Drag → Click to finish
- Good for: Palm, large finger sections

### Lasso (Recommended for fingers)
- Click → Draw freehand → Click to close
- Good for: Individual fingers, curved areas

### Click (single)
- Click directly on sensor
- Good for: Individual corrections

### Click (multi)
- Click multiple sensors to build selection
- Click again to deselect
- Good for: Scattered sensors

---

## Regions to Annotate

Based on your glove (165 sensors total):

1. **Thumb (大拇指)** - Red
2. **Index (食指)** - Green  
3. **Middle (中指)** - Blue
4. **Ring (无名指)** - Yellow
5. **Little (小拇指)** - Purple
6. **Palm (手掌)** - Cyan

**Note:** No finger backs (previous code had this by mistake)

---

## Expected Sensor Distribution

Rough estimate for 165 sensors:
- Each finger: ~15-20 sensors (75-100 total)
- Palm: ~65-90 sensors
- **Total: 165 sensors**

Your actual distribution may vary based on glove design!

---

## Output Format

The saved CSV will look like:
```csv
sensor_id,x_mm,y_mm,region
1,63.743,247.982,thumb
2,55.219,247.921,thumb
3,59.875,247.916,thumb
...
50,27.849,209.258,palm
...
165,39.475,105.686,palm
```

---

## Tips for Best Results

### Annotation Strategy
1. **Start with fingers** (easier to identify by position)
   - Thumb is usually rightmost
   - Little finger is usually leftmost
   - Work from tips down to base

2. **Finish with palm** (everything remaining)
   - Select large areas with rectangle
   - Clean up edges with click mode

### Visual Navigation
- **Zoom:** Mouse wheel
- **Pan:** Right-click and drag
- **Auto-fit:** Right-click → "View All"
- **Sensor IDs:** Shown every 5th sensor (to reduce clutter)

### Quality Checks
- Watch the **Statistics panel** - counts should add up to 165
- Look for **unassigned sensors** (gray) before saving
- Use **Undo** if you make mistakes
- **Save frequently** to avoid losing work

---

## Next Steps After Annotation

Once you have `glove_sensor_map_annotated.csv`:

### 1. Validate Your Work
```bash
cd playground
../.venv/bin/python -c "
import pandas as pd
df = pd.read_csv('glove_sensor_map_annotated.csv')
print(df['region'].value_counts())
print(f'Total: {len(df)}')
"
```

### 2. Integrate with Visualization
Update `hand_visualizer.py` to:
- Load annotated CSV instead of using hard-coded positions
- Use actual sensor coordinates
- Group by region for better layout

### 3. Test with Real Glove
- Run the visualization app
- Press each finger
- Verify correct sensors light up
- Adjust annotations if needed

---

## Troubleshooting

### Tool won't start
```bash
# Check dependencies
cd playground
../.venv/bin/python -c "import pandas, PyQt5, pyqtgraph; print('OK')"
```

### Selection not working
- Make sure you **click twice** (start → finish)
- Try different selection mode
- Check status bar for instructions

### Can't save CSV
- Check file permissions
- Choose different directory
- Make sure all sensors are assigned (or accept the warning)

### Colors not updating
- Selection might be empty
- Try clearing and reselecting
- Check that you clicked a region button

---

## Architecture Notes

### Key Components

**SensorAnnotationTool (QMainWindow)**
- Main application window
- Manages state and UI layout

**PyQtGraph PlotWidget**
- Displays sensors as scatter plot
- Handles zoom/pan/mouse interaction

**Selection Logic**
- Rectangle: Bounding box containment
- Lasso: Point-in-polygon algorithm
- Click: Nearest neighbor search

**Data Management**
- Uses pandas DataFrame
- Maintains `assignments` dict (sensor_id → region)
- History stack for undo

---

## Code Structure

```
annotate_sensors.py (600+ lines)
├── REGIONS dict - Region definitions with colors
├── SelectableScatterPlotItem - Custom scatter plot
├── SensorAnnotationTool - Main window class
│   ├── setup_ui() - Create layout
│   ├── load_csv() - Import sensor data
│   ├── plot_sensors() - Render visualization
│   ├── Selection handlers (rectangle, lasso, click)
│   ├── assign_region() - Assign sensors to region
│   ├── update_statistics() - Show counts
│   └── save_csv() - Export annotated data
└── main() - Application entry point
```

---

## Future Enhancements (Optional)

If you need more features:
- [ ] Keyboard shortcuts (1-6 for regions, Ctrl+Z for undo)
- [ ] Auto-clustering based on coordinates
- [ ] Sub-region annotation (tip, mid, base)
- [ ] Copy/paste sensor selections
- [ ] Batch operations
- [ ] Visual validation mode
- [ ] Integration with real-time viz

---

## Summary

✅ **Complete interactive annotation tool**
✅ **Easy-to-use GUI with multiple selection modes**
✅ **Saves properly formatted CSV for downstream use**
✅ **Well documented with step-by-step guide**
✅ **Ready to use right now!**

**Time to annotate:** ~10-15 minutes for 165 sensors

Go ahead and run it! 🚀

```bash
cd playground
./run_annotation_tool.sh
```

Then load `glove_sensor_map_refined.csv` and start annotating!

