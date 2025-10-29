# Acquisition Process Testing Guide

Quick guide to test the new multiprocessing-based acquisition system.

---

## Prerequisites

1. **Glove connected** to USB
2. **Port identified**: `/dev/cu.usbmodem57640302171` (or check with `ls /dev/cu.*`)
3. **No other programs** using the port (close old GUI if running)

---

## Test 1: Simple Standalone Test ⭐ START HERE

**Run in your terminal:**
```bash
cd playground
python3 acquisition_process.py /dev/cu.usbmodem57640302171
```

**Expected Output:**
```
============================================================
Acquisition Process Test
============================================================
[Acquisition] Connected to /dev/cu.usbmodem57640302171
Started acquisition process (PID: 12345)

Frames:     87 | Rate:  200.3 Hz | Queue:    0 | Time:    0.4s
Frames:    287 | Rate:  201.1 Hz | Queue:    2 | Time:    1.4s
Frames:    489 | Rate:  200.8 Hz | Queue:    1 | Time:    2.4s
...
```

**What to Check:**
- ✅ Rate is ~200 Hz (not 76 Hz!)
- ✅ Queue depth stays low (< 10)
- ✅ Frames continuously increasing
- ✅ No error messages

**Stop:** Press `Ctrl+C`

**Success Criteria:**
```
Test Results:
  Total frames: 2000+
  Duration: 10.0 seconds
  Average rate: 200+ Hz  ← IMPORTANT!
```

---

## Test 2: Performance Test (10 seconds)

**More detailed test with statistics:**
```bash
cd playground
python3 test_acquisition_performance.py /dev/cu.usbmodem57640302171 10
```

**Expected Output:**
```
Acquisition Performance Test
============================================================
Port: /dev/cu.usbmodem57640302171
Duration: 10 seconds
Target: 200+ Hz
============================================================

✓ Acquisition process started

Frames:    201 | Rate:  201.0 Hz | Queue:    0 (max:    2) | Time:   1.0s
Frames:    402 | Rate:  201.0 Hz | Queue:    1 (max:    3) | Time:   2.0s
...

Test Results:
============================================================
  Total frames captured: 2010
  Test duration: 10.00 seconds
  Average capture rate: 201.0 Hz
  Max queue depth: 5

✅ SUCCESS: Achieved target rate (200+ Hz)
✅ Queue depth good (< 100 frames)
```

**Success Criteria:**
- ✅ Average rate: **200+ Hz** (vs 76 Hz before!)
- ✅ Max queue depth: **< 100 frames**
- ✅ No "FAILED" messages

---

## Test 3: Longer Stress Test (1 minute)

**Test for sustained performance:**
```bash
cd playground
python3 test_acquisition_performance.py /dev/cu.usbmodem57640302171 60
```

**What to Check:**
- ✅ Rate stays consistent (no degradation)
- ✅ Queue doesn't grow unbounded
- ✅ No crashes or errors

---

## Troubleshooting

### "No such file or directory"
**Problem:** Serial port not found

**Solutions:**
1. Check if glove is connected:
   ```bash
   ls /dev/cu.usbmodem*
   ```

2. Try the correct port name from the list

3. Check USB cable connection

---

### "Permission denied"
**Problem:** No permission to access serial port

**Solution:**
```bash
sudo chmod 666 /dev/cu.usbmodem57640302171
```
Or add your user to dialout group (Linux only)

---

### "Port already in use"
**Problem:** Another program is using the port

**Solutions:**
1. Close the old GUI:
   ```bash
   pkill -f realtime_glove_viz
   ```

2. Check what's using it:
   ```bash
   lsof /dev/cu.usbmodem57640302171
   ```

---

### Rate is only ~76 Hz (same as before)
**Problem:** Still using old threading approach

**Check:** Make sure you're running `acquisition_process.py`, not the old GUI

---

### Queue depth keeps growing
**Problem:** Consumer too slow or not consuming

**This is expected** in standalone test if you're just testing the acquisition side. The queue will fill up to 1000 frames and then drop frames. This is OK - it means acquisition is working at full speed!

---

## What Success Looks Like

### Before (QThread with GIL):
```
Capture: ~76 Hz
Display: 10 Hz
Queue: Limited to 10 frames
```

### After (Multiprocessing):
```
Capture: ~200 Hz ✅ (2.6x improvement!)
Display: 10 Hz (unchanged, as intended)
Queue: Up to 1000 frames (50x larger buffer)
```

---

## Next Steps After Testing

Once you confirm **200+ Hz** capture:

1. **✅ Standalone acquisition works** - This test
2. **⏳ Integrate with GUI** - Replace SerialReaderThread
3. **⏳ Add monitoring** - Health checks, auto-restart
4. **⏳ Profile** - CPU/memory usage validation

---

## Quick Commands Summary

```bash
# Test 1: Basic standalone (recommended start)
python3 acquisition_process.py /dev/cu.usbmodem57640302171

# Test 2: 10-second performance test
python3 test_acquisition_performance.py /dev/cu.usbmodem57640302171 10

# Test 3: 1-minute stress test
python3 test_acquisition_performance.py /dev/cu.usbmodem57640302171 60

# Check if port exists
ls /dev/cu.usb*

# Check if port is in use
lsof /dev/cu.usbmodem57640302171
```

---

**Ready to test! Start with Test 1, then move to Test 2.** 🚀
