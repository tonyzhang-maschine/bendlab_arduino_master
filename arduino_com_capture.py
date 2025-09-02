#!/usr/bin/env python3

import click
import yaml
import logging
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from typing import Optional

from src.serial_manager import SerialManager
from src.data_processor import DataProcessor
from src.output_handlers import CLIDisplay, LSLOutput, MockDataGenerator

console = Console()

def setup_logging(config: dict):
    log_config = config.get('logging', {})
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_config.get('file', 'arduino_com.log')),
            logging.StreamHandler()
        ]
    )

def load_config(config_path: str) -> dict:
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Failed to load config: {e}[/red]")
        return {}

def select_com_port(serial_manager: SerialManager) -> Optional[str]:
    console.print("\n[cyan]Scanning for available COM ports...[/cyan]")
    
    ports = serial_manager.list_available_ports()
    arduino_ports = serial_manager.detect_arduino_ports()
    
    if not ports:
        console.print("[red]No COM ports detected![/red]")
        return None
    
    table = Table(title="Available COM Ports")
    table.add_column("Index", style="cyan", no_wrap=True)
    table.add_column("Port", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Arduino", style="yellow")
    
    for idx, port in enumerate(ports, 1):
        is_arduino = "Yes" if port in arduino_ports else "No"
        table.add_row(str(idx), port.port, port.description, is_arduino)
    
    console.print(table)
    
    if arduino_ports:
        console.print(f"\n[green]Detected {len(arduino_ports)} Arduino device(s)[/green]")
        if Confirm.ask("Use auto-detected Arduino port?"):
            return arduino_ports[0].port
    
    while True:
        choice = Prompt.ask("\nSelect port by index or enter port name directly", default="")
        
        if not choice:
            return None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                return ports[idx].port
        except ValueError:
            if any(p.port == choice for p in ports):
                return choice
        
        console.print("[red]Invalid selection. Please try again.[/red]")

def select_output_mode() -> str:
    console.print("\n[cyan]Select output mode:[/cyan]")
    console.print("1. Display to CLI only")
    console.print("2. Display to CLI and send to LSL")
    console.print("3. Mock data mode (for testing)")
    console.print("4. Mock data mode with LSL output")
    
    while True:
        choice = Prompt.ask("Enter choice [1-4]", default="1")
        if choice in ["1", "2", "3", "4"]:
            return choice
        console.print("[red]Invalid choice. Please enter 1, 2, 3, or 4.[/red]")

@click.command()
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file')
@click.option('--port', '-p', help='COM port to use (e.g., COM3 or /dev/ttyUSB0)')
@click.option('--mode', '-m', type=click.Choice(['1', '2', '3']), help='Output mode: 1=CLI, 2=CLI+LSL, 3=Mock')
@click.option('--mock', is_flag=True, help='Use mock data mode')
def main(config, port, mode, mock):
    console.print("[bold cyan]Arduino BLE 33 Data Capture System[/bold cyan]")
    console.print("=" * 50)
    
    config_data = load_config(config)
    setup_logging(config_data)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Arduino data capture system")
    
    serial_manager = SerialManager(config_data)
    data_processor = DataProcessor(config_data)
    cli_display = CLIDisplay(config_data)
    lsl_output = None
    mock_generator = None
    
    if mock:
        mode = '3'
    
    if not mode:
        mode = select_output_mode()
    
    use_mock = (mode == '3' or mode == '4')
    use_lsl = (mode == '2' or mode == '4')
    
    if use_lsl:
        lsl_output = LSLOutput(config_data)
    
    if use_mock:
        mock_generator = MockDataGenerator(config_data)
    
    def on_serial_data(data_packet):
        data_processor.add_data(data_packet)
    
    def on_processed_data(processed_data):
        cli_display.update_data(processed_data)
        if use_lsl and lsl_output:
            lsl_output.send_data(processed_data)
    
    def on_connection_change(connected: bool, port_name: str):
        cli_display.update_connection_status(connected, port_name)
        if connected:
            console.print(f"\n[green]Successfully connected to {port_name}[/green]")
        else:
            console.print(f"\n[red]Disconnected from {port_name}[/red]")
    
    def on_error(error_msg: str):
        console.print(f"\n[red]Error: {error_msg}[/red]")
    
    serial_manager.set_callbacks(
        data_callback=on_serial_data,
        error_callback=on_error,
        connection_callback=on_connection_change
    )
    
    data_processor.set_callbacks(
        process_callback=on_processed_data,
        error_callback=on_error
    )
    
    data_processor.start()
    cli_display.start()
    
    if use_lsl and lsl_output:
        if not lsl_output.start():
            console.print("[yellow]Warning: LSL output could not be started[/yellow]")
            use_lsl = False
    
    try:
        if use_mock:
            console.print("\n[yellow]Starting in MOCK DATA mode[/yellow]")
            cli_display.update_connection_status(True, "MOCK")
            mock_generator.start(on_serial_data)
            console.print("[green]Mock data generator started[/green]")
            console.print("\n[dim]Press Ctrl+C to stop...[/dim]")
            
        else:
            if not port:
                port = select_com_port(serial_manager)
            
            if not port:
                console.print("[red]No port selected. Exiting.[/red]")
                return
            
            console.print(f"\n[cyan]Attempting to connect to {port}...[/cyan]")
            
            if serial_manager.connect(port):
                console.print(f"[green]Connected successfully![/green]")
                console.print("\n[dim]Press Ctrl+C to stop...[/dim]")
            else:
                console.print("[red]Failed to connect. Please check the port and try again.[/red]")
                
                if Confirm.ask("Would you like to try another port?"):
                    port = select_com_port(serial_manager)
                    if port and serial_manager.connect(port):
                        console.print(f"[green]Connected successfully![/green]")
                        console.print("\n[dim]Press Ctrl+C to stop...[/dim]")
                    else:
                        console.print("[red]Connection failed. Exiting.[/red]")
                        return
                else:
                    return
        
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
        
    finally:
        if mock_generator:
            mock_generator.stop()
        
        serial_manager.disconnect()
        data_processor.stop()
        cli_display.stop()
        
        if lsl_output:
            lsl_output.stop()
        
        console.print("[green]Shutdown complete.[/green]")
        logger.info("Arduino data capture system stopped")

if __name__ == "__main__":
    main()