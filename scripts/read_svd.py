import xml.etree.ElementTree as ET
import sys
import os

def parse_svd(svd_file, peripheral_name, register_name=None):
    if not os.path.exists(svd_file):
        print(f"Error: SVD file '{svd_file}' not found.")
        return

    try:
        tree = ET.parse(svd_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing SVD file: {e}")
        return

    # Find peripheral
    peripheral = None
    for p in root.findall(".//peripheral"):
        name = p.find("name").text
        if name == peripheral_name:
            peripheral = p
            break
    
    if not peripheral:
        print(f"Peripheral '{peripheral_name}' not found.")
        return

    base_address = int(peripheral.find("baseAddress").text, 16)
    print(f"Peripheral: {peripheral_name} (Base: 0x{base_address:08X})")

    registers = peripheral.find("registers")
    if registers is None:
        print("No registers found.")
        return

    if register_name:
        # Find specific register
        reg = None
        for r in registers.findall("register"):
            name = r.find("name").text
            if name == register_name:
                reg = r
                break
        
        if not reg:
            print(f"Register '{register_name}' not found in {peripheral_name}.")
            return

        offset = int(reg.find("addressOffset").text, 16)
        address = base_address + offset
        print(f"Register: {register_name} (Address: 0x{address:08X})")
        
        description = reg.find("description")
        if description is not None:
            print(f"Description: {description.text.strip()}")

        fields = reg.find("fields")
        if fields is not None:
            print("Fields:")
            for f in fields.findall("field"):
                fname = f.find("name").text
                bit_offset = int(f.find("bitOffset").text)
                bit_width = int(f.find("bitWidth").text)
                desc = f.find("description")
                desc_text = desc.text.strip() if desc is not None else ""
                print(f"  {fname}: [{bit_offset + bit_width - 1}:{bit_offset}] - {desc_text}")
    else:
        # List all registers
        print("Registers:")
        for r in registers.findall("register"):
            name = r.find("name").text
            offset = int(r.find("addressOffset").text, 16)
            address = base_address + offset
            print(f"  {name:<10} (Offset: 0x{offset:04X}, Address: 0x{address:08X})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 read_svd.py <svd_file> <peripheral> [register]")
        sys.exit(1)

    svd_file = sys.argv[1]
    peripheral = sys.argv[2]
    register = sys.argv[3] if len(sys.argv) > 3 else None

    parse_svd(svd_file, peripheral, register)
