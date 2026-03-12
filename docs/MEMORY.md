### Process:
- Minecraft.Win10.DX11.exe
**Reach:**
- Minecraft.Win10.DX11.exe+B52A70

## JMP Modules
### AutoSprint:
```python
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
```
### Injection
```python
def enable_autosprint():
    """Open Minecraft process, allocate code, and patch injection point for AutoSprint."""
    global pm, inject_addr, newmem_addr, original_bytes
    
    # Check if process is open
    if pm is None:
        raise RuntimeError(texts.get("autosprint_open_first", "Process not open! Click 'Open process' first to connect to Minecraft.Win10.DX11.exe"))
    
    log_info(f"Injecting into: {PROCESS_NAME}")
    
    # If already injected, don't inject again
    if inject_addr is not None:
        log_info("AutoSprint already injected into this process")
        return
    
    try:
        module = pymem.process.module_from_name(pm.process_handle, "Minecraft.Win10.DX11.exe")
    except Exception as e:
        raise RuntimeError("Minecraft module not found in process")
    
    if not module:
        raise RuntimeError("Minecraft module not found in process")
    
    pattern = b"\x0F\xB6\x41\x63\x48\x8D\x2D\x39\xE0\xC3\x00"
    inject_addr = pm.pattern_scan_module(pattern, module)
    
    if not inject_addr:
        raise RuntimeError("Pattern not found in module; injection failed")
    
    log_info(f"{texts.get('autosprint_pattern_found', 'Found injection pattern')}: {hex(inject_addr)}")
    original_bytes = pm.read_bytes(inject_addr, len(pattern))
    
    # Try to allocate memory near the injection address
    newmem_addr = None
    use_absolute_jump = False
    
    for attempt in range(5):
        newmem_addr = allocate_near(inject_addr)
        if not newmem_addr:
            continue
        jmp_rel_test = newmem_addr - (inject_addr + 5)
        if -0x80000000 <= jmp_rel_test <= 0x7FFFFFFF:
            log_info(f"{texts.get('autosprint_memory_allocated', 'Allocated memory')}: {hex(newmem_addr)} (offset: {hex(jmp_rel_test & 0xFFFFFFFF)})")
            break
        # not usable, free and try again
        try:
            pm.free(newmem_addr)
        except:
            pass
        newmem_addr = None
    
    # If we couldn't get a close allocation, use fallback with absolute jump
    if not newmem_addr:
        log_info(texts.get("autosprint_memory_allocated_absolute", "Could not allocate within 32-bit range, using absolute jump strategy"))
        try:
            newmem_addr = pm.allocate(0x1000)
            use_absolute_jump = True
            log_info(f"{texts.get('autosprint_memory_allocated', 'Allocated memory')}: {hex(newmem_addr)}")
        except Exception as e:
            inject_addr = None
            raise RuntimeError(f"Could not allocate memory: {e}")

    try:
        # build new code block
        base = module.lpBaseOfDll
        code = bytearray()
        
        if use_absolute_jump:
            # For absolute jumps from the trampoline, we still use RIP-relative
            # mov eax,6
            code += b"\xB8\x06\x00\x00\x00"
            # lea rbp,[base+0xE63B88]
            target_ptr = base + 0xE63B88
            cur = newmem_addr + len(code)
            rel = target_ptr - (cur + 7)
            code += b"\x48\x8D\x2D" + rel.to_bytes(4, "little", signed=True)
            # jmp back using absolute jump
            return_addr = inject_addr + len(pattern)
            # movabs rax, return_addr
            code += b"\x48\xB8" + return_addr.to_bytes(8, "little")
            # jmp rax
            code += b"\xFF\xE0"
        else:
            # mov eax,6
            code += b"\xB8\x06\x00\x00\x00"
            # lea rbp,[base+0xE63B88]
            target_ptr = base + 0xE63B88
            cur = newmem_addr + len(code)
            rel = target_ptr - (cur + 7)
            code += b"\x48\x8D\x2D" + rel.to_bytes(4, "little", signed=True)
            # jmp back to return address (end of overwritten bytes)
            return_addr = inject_addr + len(pattern)
            cur = newmem_addr + len(code)
            rel = return_addr - (cur + 5)
            code += b"\xE9" + rel.to_bytes(4, "little", signed=True)
        
        pm.write_bytes(newmem_addr, bytes(code), len(code))
        log_info(f"Wrote {len(code)} bytes to {hex(newmem_addr)}")
        
        # Patch injection point
        if use_absolute_jump:
            # Use absolute jump: movabs rax, newmem_addr; jmp rax
            patch = bytearray()
            patch += b"\x48\xB8" + newmem_addr.to_bytes(8, "little")
            patch += b"\xFF\xE0"
            # Pad with nops to match or exceed pattern size
            while len(patch) < len(pattern):
                patch += b"\x90"
            pm.write_bytes(inject_addr, bytes(patch[:len(pattern)]), len(pattern))
            log_info(f"Patched with absolute jump at {hex(inject_addr)}")
        else:
            # Use relative jump
            jmp_rel = newmem_addr - (inject_addr + 5)
            patch = b"\xE9" + jmp_rel.to_bytes(4, "little", signed=True) + b"\x90" * (len(pattern) - 5)
            pm.write_bytes(inject_addr, patch, len(patch))
            log_info(f"Patched with relative jump at {hex(inject_addr)}")
        
        log_info(f"[+] AutoSprint injected successfully!")
    except Exception as e:
        inject_addr = None
        if newmem_addr:
            try:
                pm.free(newmem_addr)
                newmem_addr = None
            except:
                pass
        raise RuntimeError(f"Injection failed: {e}")

```

### Hitbox:
```py
inject_addr_hb = None
newmem_addr_hb = None
original_bytes_hb = None
```
- Injection
```py
def enable_hitbox():
    """Open Minecraft process, allocate code, and patch injection point for Hitbox control."""
    global pm, inject_addr_hb, newmem_addr_hb, original_bytes_hb
    if pm is None:
        raise RuntimeError("Process not open. Open process first.")
    if inject_addr_hb is not None:
        log_info("Hitbox already injected")
        return
    try:
        module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME)
    except Exception:
        raise RuntimeError("Minecraft module not found in process")
    if not module:
        raise RuntimeError("Minecraft module not found in process")

    inject_addr_hb = module.lpBaseOfDll + 0x4B57B0
    log_info(f"Using direct offset for hitbox: {hex(inject_addr_hb)}")

    try:
        original_bytes_hb = pm.read_bytes(inject_addr_hb, 8)
        log_info(f"Original bytes read: {original_bytes_hb.hex()}")
    except Exception as e:
        log_info(f"Could not read original bytes, assuming pattern: {e}")
        original_bytes_hb = b"\xF3\x0F\x10\x81\xD0\x00\x00\x00"

    # allocate near
    newmem_addr_hb = None
    for attempt in range(8):
        addr = allocate_near(inject_addr_hb)
        if not addr:
            continue
        jmp_rel = addr - (inject_addr_hb + 5)
        if -0x80000000 <= jmp_rel <= 0x7FFFFFFF:
            newmem_addr_hb = addr
            log_info(f"Allocated hitbox trampoline at {hex(newmem_addr_hb)}")
            break
        try:
            pm.free(addr)
        except:
            pass

    if not newmem_addr_hb:
        try:
            newmem_addr_hb = pm.allocate(0x1000)
            log_info(f"Fallback allocated hitbox memory at {hex(newmem_addr_hb)}")
        except Exception as e:
            inject_addr_hb = None
            raise RuntimeError(f"Could not allocate memory for hitbox: {e}")

    # build shellcode: mov eax, <float_int>; mov [rcx+0xD0], eax; original movss; jmp back
    code = bytearray()
    # default float 0.6
    val = 0.6
    fv = struct.pack('<f', val)
    code += b"\xB8" + int.from_bytes(fv, 'little').to_bytes(4, 'little')
    code += b"\x89\x81\xD0\x00\x00\x00"
    code += b"\xF3\x0F\x10\x81\xD0\x00\x00\x00"
    # jmp back to inject+8
    return_addr = inject_addr_hb + 8
    rel = return_addr - (newmem_addr_hb + len(code) + 5)
    code += b"\xE9" + rel.to_bytes(4, 'little', signed=True)

    pm.write_bytes(newmem_addr_hb, bytes(code), len(code))
    log_info(f"Wrote hitbox shellcode ({len(code)} bytes) to {hex(newmem_addr_hb)}")

    # patch original
    try:
        jmp_rel = newmem_addr_hb - (inject_addr_hb + 5)
        patch = b"\xE9" + jmp_rel.to_bytes(4, 'little', signed=True) + b"\x90\x90\x90"
        pm.write_bytes(inject_addr_hb, patch, len(patch))
        log_info(f"Patched hitbox injection point at {hex(inject_addr_hb)}")
    except Exception as e:
        if newmem_addr_hb:
            try:
                pm.free(newmem_addr_hb)
            except:
                pass
        inject_addr_hb = None
        newmem_addr_hb = None
        raise RuntimeError(f"Failed to patch hitbox point: {e}")
```

### Speed
```python
speed_value_addr = None
inject_addr_speed = None
newmem_addr_speed = None
original_bytes_speed = None
speed_backup_addr = None  # Backup address for value persistence after disable
```

- Injection

```py
def enable_movement():
    """Enable Movement Speed with code injection (like Hitbox)."""
    global pm, speed_value_addr, inject_addr_speed, newmem_addr_speed, original_bytes_speed

    if pm is None:
        raise RuntimeError("Process not open!")

    if inject_addr_speed is not None:
        log_info("Movement Speed already injected")
        return

    try:
        module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME)
    except Exception:
        raise RuntimeError("Minecraft module not found in process")

    if not module:
        raise RuntimeError("Minecraft module not found in process")

    # Use direct offset (same pattern as Hitbox)
    inject_addr_speed = module.lpBaseOfDll + 0x4FC02D
    log_info(f"Using offset for Movement Speed: {hex(inject_addr_speed)}")

    try:
        original_bytes_speed = pm.read_bytes(inject_addr_speed, 8)
        log_info(f"Original bytes read: {original_bytes_speed.hex()}")
    except Exception as e:
        log_info(f"Could not read original bytes: {e}")
        original_bytes_speed = b"\xF3\x0F\x10\x80\x84\x00\x00\x00"

    # Allocate memory for speed value
    speed_value_addr = pm.allocate(4)
    val = 0.135
    fv = struct.pack('<f', val)
    pm.write_bytes(speed_value_addr, fv, 4)
    log_info(f"Speed value allocated at: {hex(speed_value_addr)}")

    # Allocate trampoline
    newmem_addr_speed = None
    for attempt in range(8):
        addr = allocate_near(inject_addr_speed)
        if not addr:
            continue
        jmp_rel = addr - (inject_addr_speed + 5)
        if -0x80000000 <= jmp_rel <= 0x7FFFFFFF:
            newmem_addr_speed = addr
            log_info(f"Allocated trampoline at {hex(newmem_addr_speed)}")
            break
        try:
            pm.free(addr)
        except:
            pass

    if not newmem_addr_speed:
        try:
            newmem_addr_speed = pm.allocate(0x1000)
            log_info(f"Fallback allocated at {hex(newmem_addr_speed)}")
        except Exception as e:
            inject_addr_speed = None
            raise RuntimeError(f"Memory allocation failed: {e}")

    # Build shellcode with absolute 64-bit addressing
    code = bytearray()
    base_addr = newmem_addr_speed
    
    # movabs r8, speed_value_addr (load 64-bit absolute address into r8)
    # This is: 49 B8 <8-byte address>
    code += b"\x49\xB8" + speed_value_addr.to_bytes(8, 'little')
    
    # movss xmm0, [r8] (load float from address into xmm0)
    # This is: F3 41 0F 10 00
    code += b"\xF3\x41\x0F\x10\x00"
    
    # movss [rax + 0x84], xmm0 (write value back to sync with original location)
    # This is: F3 0F 11 80 84 00 00 00
    code += b"\xF3\x0F\x11\x80\x84\x00\x00\x00"
    
    # jmp back to return address
    # The offset is from the next instruction (base_addr + len(code) + 5)
    return_addr = inject_addr_speed + 8
    jmp_offset = return_addr - (base_addr + len(code) + 5)
    code += b"\xE9" + jmp_offset.to_bytes(4, 'little', signed=True)

    pm.write_bytes(newmem_addr_speed, bytes(code), len(code))
    log_info(f"Shellcode written ({len(code)} bytes)")

    # Patch injection point with JMP to trampoline
    try:
        jmp_rel = newmem_addr_speed - (inject_addr_speed + 5)
        patch = b"\xE9" + jmp_rel.to_bytes(4, 'little', signed=True) + b"\x90\x90\x90"
        pm.write_bytes(inject_addr_speed, bytes(patch), 8)
        log_info(f"Patched injection point at {hex(inject_addr_speed)}")
        log_info("[+] Movement Speed injected successfully!")
    except Exception as e:
        if newmem_addr_speed:
            try:
                pm.free(newmem_addr_speed)
            except:
                pass
        inject_addr_speed = None
        raise RuntimeError(f"Failed to patch: {e}")
```

### Random Nick (String Generator) - No memory injection
```py
def generate_string():
    global hard_to_type, string_length
    if hard_to_type:
        characters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    else:
        characters = string.ascii_letters + string.digits
    cadena = ''.join(random.choice(characters) for _ in range(string_length))
    dpg.set_value("string_input", cadena)

def reload_string():
    generate_string()

def toggle_hard_to_type(sender, app_data):
    global hard_to_type, texts
    hard_to_type = app_data
    if hard_to_type:
        dpg.configure_item("hard_to_type_btn", label=texts.get("hard_to_type_on", "Make harder to type: ON"))
    else:
        dpg.configure_item("hard_to_type_btn", label=texts.get("hard_to_type_off", "Make harder to type: OFF"))
    generate_string()

def copy_string():
    global texts
    text = dpg.get_value("string_input")
    dpg.set_clipboard_text(text)
    log_info(texts.get("string_copied", "String copied to clipboard"))
```
