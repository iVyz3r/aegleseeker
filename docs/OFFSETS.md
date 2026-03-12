# 📍 Aegleseeker - Offsets Documentation

Complete documentation of all offsets, memory addresses and patterns used in Aegleseeker Client v1.1.71

---

## 🎯 Main Offsets

| Variable | Offset | Description | Type |
|----------|--------|-------------|------|
| **OFFSET_REACH** | `0xB52A70` | Reach control address | Base + Offset |
| **Hitbox Injection** | `0x4B57B0` | Hitbox control injection point | Base + Offset |
| **Movement Speed** | `0x4FC02D` | Movement speed injection point | Base + Offset |
| **AutoSprint Target** | `0xE63B88` | AutoSprint target pointer | Base + Offset |

---

## 🔧 Shellcode Offsets

### Hitbox Control
```
Offset: 0xD0
Usage: mov [rcx+0xD0], eax
Context: Hitbox value storage in register
```

### Movement Speed
```
Offset: 0x84
Usage: movss [rax + 0x84], xmm0
Context: Movement speed value write
```

### FullBright
```
Offset: 0x1A0 (0xA0 internal)
Usage: movss xmm0,[rax+0x000001A0]
Context: Brightness value read
```

---

## 🔍 Byte Patterns (Pattern Scanning)

### AutoSprint
```
Pattern: 0F B6 41 63 48 8D 2D 39 E0 C3 00
Description: AutoSprint injection pattern
Location: Minecraft.Win10.DX11.exe module
```

### FullBright
```
Pattern: F3 0F 10 80 A0 01 00 00
Description: Full brightness control pattern
Location: Minecraft.Win10.DX11.exe module
```

### Hitbox
```
Pattern: F3 0F 10 81 D0 00 00 00 C3
Description: Hitbox control pattern
Location: Minecraft.Win10.DX11.exe module
```

### Movement Speed
```
Pattern: 9C F4 FF F3 0F 10 80 84 00 00 00
Description: Movement speed pattern
Location: Minecraft.Win10.DX11.exe module
```

---

## 📊 Memory Constants

| Constant | Value | Description |
|-----------|-------|----------|
| `PAGE_EXECUTE_READWRITE` | `0x40` | Memory protection (Execute + Read + Write) |
| `MEM_COMMIT` | `0x1000` | Memory commit size |
| `MEM_RESERVE` | `0x2000` | Memory reserve size |

---

## 🎮 Process Information

| Property | Value |
|-----------|-------|
| **Process Name** | `Minecraft.Win10.DX11.exe` |
| **App Version** | `v1.1.71` |
| **Author** | `iVyz3r_` |
| **Default Discord Client** | `000` |

---

## 🛠️ Global Variables for Injection

### AutoSprint
```python
inject_addr = None              # Injection address
newmem_addr = None              # New memory address
original_bytes = None           # Original bytes saved
```

### FullBright
```python
inject_addr_fb = None           # FullBright injection address
newmem_addr_fb = None           # FullBright new memory address
original_bytes_fb = None        # FullBright original bytes
```

### Hitbox
```python
inject_addr_hb = None           # Hitbox injection address
newmem_addr_hb = None           # Hitbox new memory address
original_bytes_hb = None        # Hitbox original bytes
```

### Movement Speed
```python
speed_value_addr = None         # Speed value address
inject_addr_speed = None        # Speed injection address
newmem_addr_speed = None        # Speed new memory address
original_bytes_speed = None     # Speed original bytes
speed_backup_addr = None        # Speed backup address
```

---

## 📝 Shellcode Patterns

### Hitbox Shellcode (Structure)

```assembly
; mov eax, <float_int>
B8 [4-byte float]

; mov [rcx+0xD0], eax
89 81 D0 00 00 00

; original movss
F3 0F 10 81 D0 00 00 00

; jmp back to inject+8
E9 [4-byte relative offset]
```

### Movement Speed Shellcode (Structure)

```assembly
; movabs r8, speed_value_addr (64-bit absolute)
49 B8 [8-byte address]

; movss xmm0, [r8]
F3 41 0F 10 00

; movss [rax + 0x84], xmm0
F3 0F 11 80 84 00 00 00

; jmp back to return address
E9 [4-byte relative offset]
```

---

## 🔐 Offset Calculation Directives

### Injection Address Calculation
```python
actual_address = module.lpBaseOfDll + offset
```

### Relative Jump (JMP) Calculation
```python
jmp_offset = target_address - (current_address + 5)
patch = b"\xE9" + jmp_offset.to_bytes(4, 'little', signed=True)
```

### Valid Range for Relative JMP
```
-0x80000000 <= jmp_offset <= 0x7FFFFFFF
```

---

## 🎛️ Feature Parameters

### Reach
- **Minimum**: `3.0`
- **Maximum**: `15.0`
- **Default**: `3.0`
- **Type**: Float

### Hitbox
- **Minimum**: `0.6`
- **Maximum**: `20.0`
- **Default**: `0.6`
- **Type**: Float
- **Register Offset**: `0xD0`

### Movement Speed
- **Minimum**: `0.135`
- **Maximum**: `20.0`
- **Default**: `0.135`
- **Type**: Float
- **Register Offset**: `0x84`

---

## 🔄 Pattern Search by Feature

| Feature | Method | Pattern | Fallback |
|---|---|---|---|
| **AutoSprint** | Pattern Scan | `0x0F 0xB6 0x41 0x63...` | Manual calculation |
| **FullBright** | Pattern Scan | `0xF3 0x0F 0x10 0x80...` | Manual calculation |
| **Hitbox** | Direct Offset | `0x4B57B0` | N/A |
| **Movement** | Direct Offset | `0x4FC02D` | N/A |

---

## 📋 Validation Checklist

- [ ] REACH Offset correct: `0xB52A70`
- [ ] Hitbox Offset valid: `0x4B57B0`
- [ ] Movement Offset valid: `0x4FC02D`
- [ ] AutoSprint target: `0xE63B88`
- [ ] Byte patterns correct
- [ ] Memory protection adequate: `PAGE_EXECUTE_READWRITE`
- [ ] Internal offsets within JMP range

---

## ⚠️ Important Notes

1. **Minecraft Version**: Offsets are optimized for `Minecraft.Win10.DX11.exe`
2. **Version Changes**: Minecraft updates may invalidate these offsets
3. **Pattern Scanning**: Recommended for more robust injections if direct offsets fail
4. **Memory Protection**: Always use `VirtualProtectEx` before writing bytes
5. **Restoration**: Saving `original_bytes` is critical for disabling features

---

## 🔗 Function References

| Function | Offsets Used |
|---------|-------------------|
| `open_process()` | `OFFSET_REACH` |
| `enable_hitbox()` | `0x4B57B0`, `0xD0` |
| `enable_movement()` | `0x4FC02D`, `0x84` |
| `enable_fullbright()` | Pattern scan `0xA0` |
| `enable_autosprint()` | Pattern scan `0xE63B88` |

---

**Last Update**: March 11, 2026  
**Version**: v1.1.71  
**Author**: iVyz3r_  
**License**: GPL-3.0
