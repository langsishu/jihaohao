import struct
import sys

path = 'unpackage/dist/dev/app-android/index/classes.dex'

with open(path, 'rb') as f:
    data = f.read()

# Parse DEX header
file_size = struct.unpack_from('<I', data, 32)[0]
header_size = struct.unpack_from('<I', data, 36)[0]

string_ids_size = struct.unpack_from('<I', data, 56)[0]
string_ids_off = struct.unpack_from('<I', data, 60)[0]
type_ids_size = struct.unpack_from('<I', data, 64)[0]
type_ids_off = struct.unpack_from('<I', data, 68)[0]
class_defs_size = struct.unpack_from('<I', data, 96)[0]
class_defs_off = struct.unpack_from('<I', data, 100)[0]

print(f"file_size: {file_size}")
print(f"class_defs: {class_defs_size} at offset {class_defs_off}")
print()

# Look for ClipboardService in string_ids
print("=== Strings containing 'ClipboardService' or 'UNI0AC7D75' ===")
for i in range(string_ids_size):
    off = struct.unpack_from('<I', data, string_ids_off + i * 4)[0]
    end = data.index(b'\x00', off)
    s = data[off:end].decode('utf-8', errors='replace')
    if 'ClipboardService' in s or 'UNI0AC7D75' in s:
        print(f"  string[{i}] = '{s}'")

# Check class_defs
print()
print("=== ALL class_defs ===")
for i in range(class_defs_size):
    off = class_defs_off + i * 32
    class_idx = struct.unpack_from('<I', data, off)[0]
    access_flags = struct.unpack_from('<I', data, off + 4)[0]
    superclass_idx = struct.unpack_from('<I', data, off + 8)[0]

    str_idx = struct.unpack_from('<I', data, string_ids_off + class_idx * 4)[0]
    end = data.index(b'\x00', str_idx)
    class_name = data[str_idx:end].decode('utf-8', errors='replace')

    if superclass_idx != 0xFFFFFFFF:
        str_idx2 = struct.unpack_from('<I', data, string_ids_off + superclass_idx * 4)[0]
        end2 = data.index(b'\x00', str_idx2)
        super_name = data[str_idx2:end2].decode('utf-8', errors='replace')
    else:
        super_name = "NONE"

    print(f"  [{i}] {class_name}  super={super_name}  flags=0x{access_flags:04x}")
