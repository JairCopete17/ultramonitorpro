"""
Ultra Monitor PRO
Jair Copete - 7th July 2026
"""
import subprocess
import platform
import time
from datetime import datetime
import sys
import os

def load_devices(filename):
  try:
    with open(filename, 'r') as f:
      devices = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return devices
  except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    sys.exit(1)
  except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)


def ping_device(host):
  command = ['ping', host]
  
  try:
    result = subprocess.run(
      command,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )
    return result.returncode == 0
  except subprocess.TimeoutExpired:
    return False
  except Exception:
    return False


def monitor_devices(devices, interval=60, continuous=True):
  device_status = {device: None for device in devices}
  
  print(f"=" * 60)
  print(f"                  Ultra Monitor PRO")
  print(f"=" * 60)
  print(f"Monitoring {len(devices)} device(s)")
  print(f"Press Ctrl+C to stop\n")
    
  try:
    cycle = 1
    while True:
      timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(f"\n[Cycle {cycle}] {timestamp}")
      print("-" * 60)
      
      status_changed = []
      
      for device in devices:
        is_reachable = ping_device(device)
        previous_status = device_status[device]
        device_status[device] = is_reachable
        
        status_symbol = "✓" if is_reachable else "✗"
        status_text = "UP" if is_reachable else "DOWN"
        
        if previous_status is not None and previous_status != is_reachable:
          change = "recovered" if is_reachable else "went down"
          status_changed.append(f"{device} {change}")
      
        print(f"{status_symbol} {device:<30} [{status_text}]")
    
      if status_changed:
          print("\n⚠ Status Changes:")
          for change in status_changed:
              print(f"  - {change}")
      
      up_count = sum(1 for status in device_status.values() if status)
      down_count = len(devices) - up_count
      print(f"\nSummary: {up_count} UP, {down_count} DOWN")
      
      if not continuous:
          break
      
      cycle += 1
      time.sleep(interval)
        
  except KeyboardInterrupt:
    print("\n\nMonitoring stopped by user.")
    print("\nFinal Status:")
    print("-" * 60)
    for device, status in device_status.items():
      status_text = "UP" if status else "DOWN" if status is not None else "UNKNOWN"
      print(f"{device:<30} [{status_text}]")

def main():
  devices_file = "devices.txt"
  interval = 30
  continuous = True
  
  if len(sys.argv) > 1:
    devices_file = sys.argv[1]
  if len(sys.argv) > 2:
    try:
      interval = int(sys.argv[2])
    except ValueError:
      print("Error: Interval must be an integer (seconds)")
      sys.exit(1)
  if len(sys.argv) > 3:
    continuous = sys.argv[3].lower() in ['true', 'yes', '1', 'continuous']
  
  devices = load_devices(devices_file)
  
  if not devices:
      print("Error: No devices found in the file.")
      sys.exit(1)
  
  monitor_devices(devices, interval, continuous)


if __name__ == "__main__":
    main()