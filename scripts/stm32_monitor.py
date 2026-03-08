#!/usr/bin/env python3
import argparse
import socket
import sys
import time
import re
import subprocess

def get_address_from_gdb(elf_file, expression):
    """Use GDB to resolve the address of a C expression (e.g., struct.member)."""
    # GDB batch command to print address of expression
    # print &expression
    cmd = [
        'gdb-multiarch', '--batch',
        '-ex', f'file {elf_file}',
        '-ex', f'print &({expression})'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Output format: "$1 = (Type *) 0x20000000 <symbol>"
        # We need to extract the address.
        output = result.stdout
        match = re.search(r'0x([0-9a-fA-F]+)', output)
        if match:
            return int(match.group(1), 16)
        else:
            print(f"Error resolving '{expression}': GDB output parse failed.\nOutput: {output}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running GDB: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: gdb-multiarch not found. Please install it.")
        return None

def get_type_size_from_gdb(elf_file, expression):
    """Use GDB to get the size of the type of the expression."""
    cmd = [
        'gdb-multiarch', '--batch',
        '-ex', f'file {elf_file}',
        '-ex', f'print sizeof({expression})'
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Output: "$1 = 4"
        match = re.search(r'=\s*(\d+)', result.stdout)
        if match:
            return int(match.group(1))
        return 4 # Default to 4 bytes if unsure
    except:
        return 4

def get_register_address(svd_file, peripheral, register):
    """Get the address of a register using read_svd (simplified logic here or import)."""
    # For simplicity, let's assume read_svd.py is available and use it via subprocess if import fails,
    # or just parse here. Re-using previous simple logic for robustness.
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(svd_file)
        root = tree.getroot()
        
        periph_node = None
        for p in root.findall(".//peripheral"):
            if p.find("name").text == peripheral:
                periph_node = p
                break
        
        if not periph_node:
            return None
            
        base_addr = int(periph_node.find("baseAddress").text, 16)
        
        if not register:
            return base_addr
            
        registers = periph_node.find("registers")
        if registers is None:
            return None
            
        for r in registers.findall("register"):
            if r.find("name").text == register:
                offset = int(r.find("addressOffset").text, 16)
                return base_addr + offset
    except Exception as e:
        print(f"Error parsing SVD: {e}")
    return None

def openocd_read_memory(address, width=32, count=1, host='127.0.0.1', port=6666):
    """Read memory via OpenOCD TCL port."""
    cmd = ""
    if width == 8: cmd = "mdb"
    elif width == 16: cmd = "mdh"
    else: cmd = "mdw"
    
    full_cmd = f"{cmd} 0x{address:08X} {count}"
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall((full_cmd + '\x1a').encode('utf-8'))
            data = b""
            while True:
                chunk = s.recv(1024)
                if not chunk: break
                data += chunk
                if b'\x1a' in chunk: break
            return data.decode('utf-8').strip().replace('\x1a', '')
    except Exception as e:
        print(f"Error communicating with OpenOCD: {e}")
        return None

def parse_value(response):
    """Parse OpenOCD memory read response."""
    # Response: "0x20000000: 00000000"
    if not response: return None
    try:
        parts = response.split(':')
        if len(parts) > 1:
            val_str = parts[1].strip().split()[0] # Take first value
            return int(val_str, 16)
        return None
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description="Monitor STM32 variables (including struct members) or registers")
    parser.add_argument("--elf", help="Path to ELF file (for variables)")
    parser.add_argument("--var", help="C expression to monitor (e.g. 'counter', 'my_struct.member', 'array[0]')")
    parser.add_argument("--svd", help="Path to SVD file (for registers)")
    parser.add_argument("--reg", help="Peripheral and Register (e.g. GPIOA MODER)", nargs='+')
    parser.add_argument("--type", choices=['float', 'int', 'hex'], default='hex', help="Display format")
    parser.add_argument("--interval", type=float, default=1.0, help="Update interval")
    parser.add_argument("--count", type=int, default=0, help="Number of samples")
    
    args = parser.parse_args()
    
    address = None
    name = ""
    size = 4
    
    if args.var:
        if not args.elf:
            print("Error: --elf required for --var")
            return
        
        print(f"Resolving address of '{args.var}' using GDB...")
        address = get_address_from_gdb(args.elf, args.var)
        if address is None:
            return
            
        name = args.var
        
        # Try to guess size/type if needed, or just default to 4 bytes
        # For float, we read 4 bytes and interpret as float
        size = get_type_size_from_gdb(args.elf, args.var)
        
    elif args.reg:
        if not args.svd:
            print("Error: --svd required for --reg")
            return
        peripheral = args.reg[0]
        register = args.reg[1] if len(args.reg) > 1 else None
        address = get_register_address(args.svd, peripheral, register)
        if address is None:
            print(f"Error: Register not found")
            return
        name = f"{peripheral}.{register}" if register else peripheral
    else:
        print("Error: Specify --var or --reg")
        return

    print(f"Monitoring {name} at 0x{address:08X} (Size: {size} bytes, Interval: {args.interval}s)")
    
    import struct
    
    cnt = 0
    try:
        while True:
            # Determine read width based on size
            width = 32
            if size == 1: width = 8
            elif size == 2: width = 16
            
            response = openocd_read_memory(address, width=width)
            raw_val = parse_value(response)
            
            if raw_val is not None:
                display_val = ""
                if args.type == 'float' and width == 32:
                    # Interpret integer bits as float
                    packed = struct.pack('I', raw_val)
                    val_float = struct.unpack('f', packed)[0]
                    display_val = f"{val_float:.6f}"
                elif args.type == 'int':
                    display_val = f"{raw_val}"
                else: # hex
                    display_val = f"0x{raw_val:X}"
                
                print(f"[{time.strftime('%H:%M:%S')}] {name} = {display_val}")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] {name} = Read Error")
            
            cnt += 1
            if args.count > 0 and cnt >= args.count:
                break
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
