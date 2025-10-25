"""
Glove Parser - Packet and frame parsing logic for JQ Glove data

Protocol:
- Delimiter: 0xAA 0x55 0x03 0x99
- Packet 0x01: 6 bytes header + 128 bytes payload = 134 bytes total
- Packet 0x02: 6 bytes header + 144 bytes payload = 150 bytes total
- Frame = Packet 0x01 + Packet 0x02 combined data (272 bytes)

Uses documented sensor-to-index mapping from sensor_mapping.py
"""

import numpy as np
from typing import Optional, Tuple, List
from sensor_mapping import extract_sensor_values


class GloveParser:
    # Protocol constants
    DELIMITER = bytes([0xAA, 0x55, 0x03, 0x99])
    PACKET_INDEX_01 = 0x01
    PACKET_INDEX_02 = 0x02
    SENSOR_TYPE_WB = 0x06
    
    def __init__(self):
        self.buffer = bytearray()
        self.pending_packet_01 = None
        self.frame_count = 0
        
    def find_delimiter(self, data: bytes) -> int:
        """Find position of delimiter in data. Returns -1 if not found."""
        try:
            return data.index(self.DELIMITER)
        except ValueError:
            return -1
    
    def parse_packet(self, data: bytes) -> Optional[Tuple[int, int, bytes]]:
        """
        Parse a single packet from data.
        
        Returns:
            tuple: (packet_index, sensor_type, payload) or None if invalid
        """
        if len(data) < 6:
            return None
        
        # Check delimiter
        if data[0:4] != self.DELIMITER:
            return None
        
        packet_index = data[4]
        sensor_type = data[5]
        
        # Validate packet index and extract payload
        if packet_index == self.PACKET_INDEX_01:
            if len(data) < 134:  # 6 header + 128 payload
                return None
            payload = data[6:134]
        elif packet_index == self.PACKET_INDEX_02:
            if len(data) < 150:  # 6 header + 144 payload
                return None
            payload = data[6:150]
        else:
            return None
        
        return (packet_index, sensor_type, payload)
    
    def add_data(self, data: bytes) -> List[np.ndarray]:
        """
        Add new data to buffer and extract complete frames.
        
        Returns:
            list: List of complete frames (each frame is 272-byte numpy array)
        """
        self.buffer.extend(data)
        frames = []
        
        while True:
            # Find delimiter
            delim_pos = self.find_delimiter(self.buffer)
            if delim_pos == -1:
                # No delimiter found, keep last 3 bytes in case delimiter is split
                if len(self.buffer) > 3:
                    self.buffer = self.buffer[-3:]
                break
            
            # Remove data before delimiter
            if delim_pos > 0:
                self.buffer = self.buffer[delim_pos:]
            
            # Try to parse packet
            packet_info = self.parse_packet(self.buffer)
            if packet_info is None:
                # Invalid packet, skip delimiter and continue
                self.buffer = self.buffer[4:]
                continue
            
            packet_index, sensor_type, payload = packet_info
            
            # Determine packet size
            packet_size = 134 if packet_index == self.PACKET_INDEX_01 else 150
            
            # Remove parsed packet from buffer
            self.buffer = self.buffer[packet_size:]
            
            # Handle packet based on index
            if packet_index == self.PACKET_INDEX_01:
                # Store packet 0x01, wait for 0x02
                self.pending_packet_01 = payload
            elif packet_index == self.PACKET_INDEX_02:
                # Combine with pending packet 0x01
                if self.pending_packet_01 is not None:
                    frame = self.combine_packets(self.pending_packet_01, payload)
                    frames.append(frame)
                    self.frame_count += 1
                    self.pending_packet_01 = None
            
        return frames
    
    def combine_packets(self, payload_01: bytes, payload_02: bytes) -> np.ndarray:
        """
        Combine two packet payloads into a complete frame.
        
        Args:
            payload_01: 128 bytes from packet 0x01
            payload_02: 144 bytes from packet 0x02
            
        Returns:
            numpy array of 272 bytes
        """
        frame_data = bytearray(payload_01) + bytearray(payload_02)
        return np.frombuffer(frame_data, dtype=np.uint8)
    
    def get_sensor_data(self, frame: np.ndarray) -> dict:
        """
        Extract sensor values from frame using documented mapping.
        
        Args:
            frame: 272-byte frame data
        
        Returns:
            dict: Sensor values organized by region (from sensor_mapping.py)
                 + raw_frame for backward compatibility
        """
        if len(frame) < 272:
            return {'raw_frame': frame}
        
        # Use documented sensor mapping
        sensor_data = extract_sensor_values(frame)
        sensor_data['raw_frame'] = frame
        
        return sensor_data
    
    def get_statistics(self) -> dict:
        """Get parser statistics."""
        return {
            'frame_count': self.frame_count,
            'buffer_size': len(self.buffer),
            'pending_packet': self.pending_packet_01 is not None
        }

