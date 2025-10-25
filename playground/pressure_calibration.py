#!/usr/bin/env python3
"""
Pressure Calibration Module for JQ Glove

Loads calibration data from CSV and provides ADC-to-pressure conversion
using linear interpolation. Supports multiple pressure units:
- N/cm² (Newtons per square centimeter)
- mmHg (millimeters of mercury)
- kPa (kilopascals)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Literal

# Type for pressure units
PressureUnit = Literal['N/cm2', 'mmHg', 'kPa']


class PressureCalibration:
    """
    Calibration data for converting ADC readings to pressure values.
    
    Uses linear interpolation from manufacturer-provided calibration curve.
    """
    
    def __init__(self, calibration_csv: Optional[str] = None):
        """
        Initialize calibration from CSV file.
        
        Args:
            calibration_csv: Path to calibration CSV. If None, uses default location.
        """
        if calibration_csv is None:
            # Default: look in same directory as this script
            script_dir = Path(__file__).parent
            calibration_csv = script_dir / "ADC_pressure_working_curve_JQ-160pts_sensor_array_C60510.csv"
        
        self.csv_path = Path(calibration_csv)
        self.data = None
        self.adc_values = None
        self.pressure_n_cm2 = None
        self.pressure_mmhg = None
        self.pressure_kpa = None
        
        self._load_calibration()
    
    def _load_calibration(self):
        """Load and parse calibration CSV."""
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"Calibration file not found: {self.csv_path}\n"
                "Please ensure ADC_pressure_working_curve_JQ-160pts_sensor_array_C60510.csv "
                "exists in the playground directory."
            )
        
        # Read CSV, handling spaces in column names and values
        self.data = pd.read_csv(self.csv_path)
        
        # Strip whitespace from column names
        self.data.columns = self.data.columns.str.strip()
        
        # Extract columns (strip whitespace from values too)
        self.adc_values = self.data['ADC reading'].values.astype(float)
        self.pressure_n_cm2 = self.data['Pressure in N/cm^2'].values.astype(float)
        self.pressure_mmhg = self.data['Pressure in mmHg'].values.astype(float)
        self.pressure_kpa = self.data['Pressure in kpa'].values.astype(float)
        
        print(f"✓ Loaded calibration data: {len(self.adc_values)} points from {self.csv_path.name}")
        print(f"  ADC range: {self.adc_values.min():.0f} - {self.adc_values.max():.0f}")
        print(f"  Pressure range: {self.pressure_kpa.min():.2f} - {self.pressure_kpa.max():.2f} kPa")
    
    def adc_to_pressure(
        self, 
        adc_values: np.ndarray, 
        unit: PressureUnit = 'kPa'
    ) -> np.ndarray:
        """
        Convert ADC readings to pressure values.
        
        Args:
            adc_values: Array of ADC readings (0-255)
            unit: Output pressure unit ('N/cm2', 'mmHg', or 'kPa')
        
        Returns:
            Array of pressure values in specified unit
        """
        # Select calibration curve based on unit
        if unit == 'N/cm2':
            pressure_curve = self.pressure_n_cm2
        elif unit == 'mmHg':
            pressure_curve = self.pressure_mmhg
        elif unit == 'kPa':
            pressure_curve = self.pressure_kpa
        else:
            raise ValueError(f"Unknown pressure unit: {unit}. Must be 'N/cm2', 'mmHg', or 'kPa'")
        
        # Use linear interpolation
        # np.interp handles extrapolation by clamping to boundary values
        pressure = np.interp(adc_values, self.adc_values, pressure_curve)
        
        return pressure
    
    def get_unit_info(self, unit: PressureUnit) -> dict:
        """
        Get display information for a pressure unit.
        
        Args:
            unit: Pressure unit
            
        Returns:
            dict with 'name', 'symbol', 'format' keys
        """
        unit_info = {
            'N/cm2': {
                'name': 'Newtons per square centimeter',
                'symbol': 'N/cm²',
                'format': '{:.3f}',  # 3 decimal places
            },
            'mmHg': {
                'name': 'Millimeters of mercury',
                'symbol': 'mmHg',
                'format': '{:.1f}',  # 1 decimal place
            },
            'kPa': {
                'name': 'Kilopascals',
                'symbol': 'kPa',
                'format': '{:.2f}',  # 2 decimal places
            }
        }
        return unit_info.get(unit, {})
    
    def get_pressure_range(self, unit: PressureUnit) -> tuple:
        """
        Get min/max pressure values for a unit.
        
        Args:
            unit: Pressure unit
            
        Returns:
            (min_pressure, max_pressure) tuple
        """
        if unit == 'N/cm2':
            return (self.pressure_n_cm2.min(), self.pressure_n_cm2.max())
        elif unit == 'mmHg':
            return (self.pressure_mmhg.min(), self.pressure_mmhg.max())
        elif unit == 'kPa':
            return (self.pressure_kpa.min(), self.pressure_kpa.max())
        else:
            raise ValueError(f"Unknown pressure unit: {unit}")


# Global calibration instance (lazy loaded)
_global_calibration: Optional[PressureCalibration] = None


def get_calibration() -> PressureCalibration:
    """
    Get global calibration instance (singleton pattern).
    
    Returns:
        PressureCalibration instance
    """
    global _global_calibration
    if _global_calibration is None:
        _global_calibration = PressureCalibration()
    return _global_calibration


def adc_to_pressure(
    adc_values: np.ndarray, 
    unit: PressureUnit = 'kPa'
) -> np.ndarray:
    """
    Convenience function to convert ADC to pressure using global calibration.
    
    Args:
        adc_values: Array of ADC readings (0-255)
        unit: Output pressure unit ('N/cm2', 'mmHg', or 'kPa')
    
    Returns:
        Array of pressure values in specified unit
    """
    calibration = get_calibration()
    return calibration.adc_to_pressure(adc_values, unit)


# Demonstration code
if __name__ == '__main__':
    print("=== Pressure Calibration Demo ===\n")
    
    # Load calibration
    cal = PressureCalibration()
    
    # Test some ADC values
    test_adc = np.array([0, 50, 100, 150, 200, 255])
    
    print("\nConversion Examples:")
    print(f"{'ADC':<6} {'kPa':<8} {'mmHg':<8} {'N/cm²':<8}")
    print("-" * 32)
    
    for adc in test_adc:
        kpa = cal.adc_to_pressure(np.array([adc]), 'kPa')[0]
        mmhg = cal.adc_to_pressure(np.array([adc]), 'mmHg')[0]
        n_cm2 = cal.adc_to_pressure(np.array([adc]), 'N/cm2')[0]
        print(f"{adc:<6.0f} {kpa:<8.2f} {mmhg:<8.1f} {n_cm2:<8.3f}")
    
    print("\n=== Test Complete ===")

