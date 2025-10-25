# Sensor Annotation Guide

## Overview
The annotation tool (`annotate_sensors.py`) allows you to interactively label which sensors belong to which finger/palm region.

## Quick Start

### 1. Run the Tool
```bash
cd playground
../.venv/bin/python annotate_sensors.py
```

### 2. Load Your CSV
- Click **"Load CSV"** button
- Select `glove_sensor_map_refined.csv`
- You'll see all 165 sensors plotted with their actual coordinates

## How to Annotate

### Selection Modes

**Rectangle Selection (Default):**
- Click to start rectangle
- Move mouse to adjust size
- Click again to finish
- All sensors inside rectangle are selected

**Lasso Selection:**
- Click to start drawing
- Move mouse to draw freehand shape
- Click again to close lasso
- All sensors inside lasso are selected

**Click (single):**
- Click directly on a sensor
- Only that sensor is selected

**Click (multi):**
- Click sensors one by one
- Builds up multi-selection
- Click same sensor to deselect it

### Assigning Regions

1. **Select sensors** using any method above
2. **Click a region button** to assign:
   - 🔴 Thumb (大拇指)
   - 🟢 Index (食指)
   - 🔵 Middle (中指)
   - 🟡 Ring (无名指)
   - 🟣 Little (小拇指)
   - 🔵 Palm (手掌)

3. Selected sensors will change color to match the region

### Workflow Tips

**Suggested Order:**
1. Start with **fingers** (easier to identify)
   - Use **lasso** to outline each finger tip
   - Work from tip down to base
2. Finish with **palm** (everything else)
   - Use **rectangle** for large areas

**If You Make a Mistake:**
- Click **"Undo"** to revert last assignment
- Or select sensors again and reassign to correct region
- Or **"Clear All Assignments"** to start over

### Visualization Help

- **Sensor IDs shown** every 5th sensor (to avoid clutter)
- **Hover over sensors** to see details
- **Pan:** Right-click and drag
- **Zoom:** Mouse wheel or pinch
- **Auto-fit:** Right-click plot → "View All"

### Statistics Panel

Shows real-time counts:
- Total sensors
- Sensors per region
- Percentage distribution

Use this to verify you've assigned all 165 sensors!

## Saving Your Work

### Save Annotated CSV
1. Click **"Save Annotated CSV"**
2. Choose filename (default: `glove_sensor_map_annotated.csv`)
3. File will include new `region` column:
   ```csv
   sensor_id,x_mm,y_mm,region
   1,63.743,247.982,thumb
   2,55.219,247.921,thumb
   ...
   ```

### Resume Later
- Your saved CSV includes region assignments
- Load it again to continue annotating
- Or modify existing assignments

## Expected Output

After annotation, you should have roughly:
- **Thumb:** ~15-20 sensors
- **Index:** ~15-20 sensors  
- **Middle:** ~15-20 sensors
- **Ring:** ~15-20 sensors
- **Little:** ~15-20 sensors
- **Palm:** ~60-80 sensors
- **Total:** 165 sensors

*(Exact counts depend on actual glove design)*

## Next Steps

Once you have `glove_sensor_map_annotated.csv`:

1. **Validate** the assignments visually
2. **Use in visualization** - Update `hand_visualizer.py` to load from annotated CSV
3. **Adjust positions** if needed - You can re-annotate anytime

## Troubleshooting

**"Selection not working"**
- Make sure you **click once** to start, **click again** to finish
- Try switching selection mode

**"Colors not updating"**
- Make sure sensors are selected (highlighted in red)
- Then click a region button

**"CSV won't save"**
- Check you have write permissions
- Some sensors still unassigned? Tool will warn you

**"Plot is cluttered"**
- Zoom in to see details
- Sensor ID labels shown every 5th sensor only
- Use pan/zoom to navigate

## Keyboard Shortcuts

*(Not implemented yet, but could add:)*
- Ctrl+Z: Undo
- Ctrl+S: Save
- 1-6: Quick select regions
- Esc: Clear selection

---

**Ready to annotate! 🧤✨**

The goal is to create a complete mapping so the real-time visualization can show accurate hand anatomy.

