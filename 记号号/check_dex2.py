import struct
import sys

path = 'unpackage/dist/dev/app-android/index/classes.dex'

with open(path, 'rb') as f:
    data = f.read()

string_ids_size = struct.unpack_from('<I', data, 56)[0]
string_ids_off = struct.unpack_from('<I', data, 60)[0]
type_ids_size = struct.unpack_from('<I', data, 64)[0]
type_ids_off = struct.unpack_from('<I', data, 68)[0]
class_defs_size = struct.unpack_from('<I', data, 96)[0]
class_defs_off = struct.unpack_from('<I', data, 100)[0]

print(f"class_defs: {class_defs_size} at offset {class_defs_off}")
print()

def get_str(idx):
    off = struct.unpack_from('<I', data, string_ids_off + idx * 4)[0]
    end = data.index(b'\x00', off)
    s = data[off:end].decode('utf-8', errors='replace')
    # Remove non-ASCII for clean print
    clean = ''.join(c if ord(c) < 128 else '?' for c in s)
    return clean

print("=== ALL class_defs ===")
for i in range(class_defs_size):
    off = class_defs_off + i * 32
    class_idx = struct.unpack_from('<I', data, off)[0]
    access_flags = struct.unpack_from('<I', data, off + 4)[0]
    superclass_idx = struct.unpack_from('<I', data, off + 8)[0]

    class_name = get_str(class_idx)
    if superclass_idx != 0xFFFFFFFF:
        super_name = get_str(superclass_idx)
    else:
        super_name = "NONE"

    print(f"  [{i:2d}] {class_name}")
    print(f"        super={super_name}  flags=0x{access_flags:04x}")

print()
print("=== Check if ClipboardService is a type_id ===")
for i in range(type_ids_size):
    str_idx = struct.unpack_from('<I', data, type_ids_off + i * 4)[0]
    s = get_str(str_idx)
    if 'ClipboardService' in s:
        print(f"  type_id[{i}] = '{s}'")
