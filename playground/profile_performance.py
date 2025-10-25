#!/usr/bin/env python3
"""
Performance Profiling Script for JQ Glove Visualization

Runs the application with cProfile to identify performance bottlenecks.
Generates a detailed report of function call times.

Usage:
    python profile_performance.py

The application will run normally. Press Ctrl+C or close the window to stop
and generate the profiling report.
"""

import cProfile
import pstats
import sys
from io import StringIO

def run_with_profiling():
    """Run the main application with profiling enabled."""
    print("=" * 80)
    print("JQ Glove Visualization - Performance Profiling")
    print("=" * 80)
    print("\nStarting application with profiling enabled...")
    print("Connect the glove and click 'Start' to begin capture.")
    print("Let it run for 15-30 seconds, then stop or close the window.")
    print("\nPress Ctrl+C or close window to generate profiling report.\n")
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Import and run the application
    profiler.enable()
    
    try:
        from realtime_glove_viz import main
        main()
    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt received, generating report...")
    except Exception as e:
        print(f"\n\nApplication stopped: {e}")
    finally:
        profiler.disable()
    
    # Generate profiling statistics
    print("\n" + "=" * 80)
    print("PERFORMANCE PROFILING REPORT")
    print("=" * 80)
    
    # Create stats object
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    
    # Print top 30 functions by cumulative time
    print("\n--- Top 30 Functions by Cumulative Time ---\n")
    stats.print_stats(30)
    
    # Print top 30 functions by internal time
    print("\n--- Top 30 Functions by Internal Time ---\n")
    stats.sort_stats('time')
    stats.print_stats(30)
    
    # Print callers for key functions
    print("\n--- Call Graph for update_sensors ---\n")
    stats.print_callers('update_sensors', 10)
    
    print("\n--- Call Graph for update_display ---\n")
    stats.print_callers('update_display', 10)
    
    # Save detailed report to file
    report_file = 'performance_profile_report.txt'
    with open(report_file, 'w') as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        f.write("=" * 80 + "\n")
        f.write("PERFORMANCE PROFILING REPORT - CUMULATIVE TIME\n")
        f.write("=" * 80 + "\n\n")
        stats.print_stats()
        
        stats.sort_stats('time')
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("PERFORMANCE PROFILING REPORT - INTERNAL TIME\n")
        f.write("=" * 80 + "\n\n")
        stats.print_stats()
    
    print(f"\n\nDetailed report saved to: {report_file}")
    print("=" * 80)


if __name__ == '__main__':
    run_with_profiling()

