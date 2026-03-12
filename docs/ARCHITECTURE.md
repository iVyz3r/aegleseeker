# 🏗️ Aegleseeker - System Architecture

Complete architectural documentation of the Aegleseeker Client v1.1.71 memory modification framework for Minecraft: Windows 10 Edition.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Module Structure](#module-structure)
- [Core Components](#core-components)
- [Memory Injection System](#memory-injection-system)
- [Feature Implementations](#feature-implementations)
- [UI Architecture](#ui-architecture)
- [Data Flow](#data-flow)
- [Configuration System](#configuration-system)
- [Threading Model](#threading-model)
- [Error Handling](#error-handling)
- [Dependencies](#dependencies)

---

## Overview

**Aegleseeker** is a sophisticated memory modification client for Minecraft: Windows 10 Edition that provides gameplay enhancement features through runtime code injection.

### Purpose
- Modify game behavior through direct memory manipulation
- Provide user-friendly interface for feature management
- Support multi-language environment
- Maintain clean code execution without permanent file modification

### Key Characteristics
- **Runtime Only**: No permanent modifications to game executable
- **Process-Based**: Operates on running Minecraft process
- **Pattern Scanning**: Dynamic offset discovery capability
- **Hot Patching**: Real-time feature enable/disable

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Aegleseeker Client                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │             User Interface Layer (DearPyGUI)         │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Combat Tab │ Movement │ Visuals │ Misc     │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        Application Logic Layer                       │   │
│  │  ├─ Feature Controllers                             │   │
│  │  ├─ Memory Manager                                  │   │
│  │  ├─ Configuration Handler                           │   │
│  │  └─ Theme & Localization Manager                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        Memory Injection Layer (PyMem)               │   │
│  │  ├─ Pattern Scanner                                 │   │
│  │  ├─ Memory Allocator                                │   │
│  │  ├─ Shellcode Generator                             │   │
│  │  └─ Injection Handler                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   Target Process: Minecraft.Win10.DX11.exe          │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Game Memory                                 │   │   │
│  │  │  ├─ Reach Offset (0xB52A70)                  │   │   │
│  │  │  ├─ Hitbox Offset (0x4B57B0)                 │   │   │
│  │  │  ├─ Movement Offset (0x4FC02D)               │   │   │
│  │  │  └─ AutoSprint + FullBright (Pattern Scan)   │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### Single-File Architecture

Aegleseeker is implemented as a monolithic Python module:

```
aeglemain.py (~2400 lines)
│
├── Imports & Dependencies
├── Constants & Configuration
├── Global Variables
├── Language Definitions
├── Configuration I/O
├── Logging System
├── Memory Patches (Scripts)
├── Memory Injection Functions
│   ├── AutoSprint
│   ├── FullBright
│   ├── Hitbox
│   └── Movement Speed
├── UI Components
├── Event Handlers & Callbacks
├── Theme Management
├── Localization
├── Main Application Loop
└── Entry Point
```

---

## Core Components

### 1. Memory Management Core

#### Process Handler
```python
class ProcessManager:
    - pm: Pymem instance (active process)
    - process_base: Base address of game module
    - process_id: Minecraft process ID
```

#### Address Tracking
```python
# Global address variables for each feature
reach_address        # Reach control
inject_addr_hb       # Hitbox injection point
inject_addr_speed    # Movement speed injection
inject_addr_fb       # FullBright injection
```

### 2. Feature Controllers

Each feature has a consistent implementation pattern:

```
enable_[feature]()      → Enable injection
disable_[feature]()     → Restore original bytes
[feature]_callback()    → UI event handler
[feature]_slider()      → Real-time value update
```

#### Features Implemented
1. **Reach**: Direct offset modification
2. **Hitbox**: Custom value injection with shellcode
3. **Movement Speed**: Floating-point speed multiplier
4. **AutoSprint**: Sprint state automation
5. **FullBright**: Full brightness illumination

### 3. Configuration System

```
Configuration Storage
├── Location: %APPDATA%/LVyrmC0nf1gDkgbIFie4bgva/
├── File: LVyrmEkFohf.json
│
└── Data Structure
    ├── Language Setting
    ├── Theme Colors (24+ color keys)
    ├── Discord Client ID
    ├── Feature States
    └── Display Preferences
```

### 4. UI Framework

**Technology**: DearPyGUI (Modern ImGui wrapper)

**Layout Structure**:
```
Main Window (560x935)
├── Header Section
│   ├── Connection Status
│   └── Process Connection Button
│
├── Tab Bar
│   ├── Combat Tab
│   │   ├── Hitbox Control
│   │   └── Reach Control
│   │
│   ├── Movement Tab
│   │   ├── AutoSprint
│   │   └── Speed Control
│   │
│   ├── Visuals Tab
│   │   └── FullBright
│   │
│   └── Misc Tab
│
├── Logs Section
│   ├── Log Display
│   └── Control Buttons
│
└── Settings Section
    ├── Theme Editor
    ├── Language Selector
    └── About Dialog
```

---

## Memory Injection System

### Injection Pipeline

```
1. Process Discovery
   └─→ Locate Minecraft.Win10.DX11.exe

2. Module Analysis
   └─→ Get base address of game DLL

3. Address Resolution
   ├─→ Direct Offset: reach_address = base + 0xB52A70
   └─→ Pattern Scan: scan_pattern(module, pattern_bytes)

4. Memory Allocation
   ├─→ Allocate shellcode space
   └─→ Allocate value storage

5. Shellcode Generation
   ├─→ Build machine code
   └─→ Generate relative jumps

6. Memory Protection
   └─→ Apply VirtualProtectEx permissions

7. Code Injection
   ├─→ Write shellcode to allocated memory
   └─→ Patch injection point with JMP

8. Value Synchronization
   └─→ Keep injected values in sync with UI
```

### Shellcode Architecture

#### Pattern: Code Cave + Trampoline

```
Original Code Location (0x4B57B0)
┌─────────────────────────────────┐
│  [Injected JMP] → NewMem        │  5 bytes
│  [NOP Padding]                  │  3 bytes
└─────────────────────────────────┘

New Memory Location (Allocated)
┌─────────────────────────────────┐
│  [Modified Logic]               │
│  [Original Instruction]         │
│  [JMP Back] → Original+8        │
└─────────────────────────────────┘
```

#### Memory Allocation Strategy

1. **Relative JMP (Preferred)**
   - Allocate within ±2GB of injection point
   - Use `allocate_near()` function
   - 8 attempts before fallback

2. **Absolute JMP (Fallback)**
   - Allocate anywhere in process space
   - Use 64-bit absolute addressing
   - More bytes required but always works

---

## Feature Implementations

### 1. Reach Modification

**Type**: Direct Memory Write  
**Offset**: `0xB52A70`  
**Value Type**: Float (4 bytes)  
**Range**: 3.0 - 15.0

```python
def set_reach(value: float):
    pm.write_float(reach_address, value)
```

### 2. Hitbox Control

**Type**: Code Injection + Shellcode  
**Injection Point**: `0x4B57B0`  
**Register Offset**: `0xD0`  
**Range**: 0.6 - 20.0

**Shellcode**:
```assembly
mov eax, <float_value>
mov [rcx+0xD0], eax
movss xmm0, [rcx+0xD0]
jmp back
```

### 3. Movement Speed

**Type**: Code Injection + Absolute Addressing  
**Injection Point**: `0x4FC02D`  
**Target Offset**: `0x84`  
**Range**: 0.135 - 20.0

**Shellcode**:
```assembly
movabs r8, speed_value_addr
movss xmm0, [r8]
movss [rax+0x84], xmm0
jmp back
```

### 4. AutoSprint

**Type**: Pattern-Scanned Injection  
**Pattern**: `0F B6 41 63 48 8D 2D 39 E0 C3 00`  
**Function**: Simulate constant sprint state

### 5. FullBright

**Type**: Pattern-Scanned Injection  
**Pattern**: `F3 0F 10 80 A0 01 00 00`  
**Function**: Override brightness calculation

---

## UI Architecture

### Component Hierarchy

```
Application
├── Context (DearPyGUI)
├── Viewport (Window Container)
│
└── Main Window
    ├── Font Registry
    ├── Header Elements
    ├── Tab Bar
    ├── Dynamic Dialogs
    │   ├── Theme Editor Modal
    │   ├── Language Modal
    │   ├── RPC ID Modal
    │   └── Client Info Modal
    │
    └── Event System
        ├── Callbacks
        ├── Handlers
        └── State Management
```

### Callback Pattern

All UI interactions use callback functions:

```python
def feature_toggle_callback(sender, app_data, user_data):
    """Standard callback signature for all UI events"""
    enabled = app_data
    try:
        if enabled:
            enable_feature()
        else:
            disable_feature()
    except Exception as e:
        log_error(str(e))
```

### Theme System

**Dynamic Color Management**:
- 24+ theme colors with fallback values
- Theme saved to configuration
- Real-time application without restart
- Random theme generator

---

## Data Flow

### Reach Modification Flow

```
User Input (Slider/Text)
    ↓
set_reach_from_slider() / set_reach()
    ↓
Validate Range (3.0 - 15.0)
    ↓
write_memory(reach_address, value)
    ↓
VirtualProtectEx() ← Memory Protection
    ↓
pm.write_float()
    ↓
VirtualProtectEx() ← Restore Protection
    ↓
log_info("Reach set to: X.XX")
    ↓
UI Update (Mirror value in display)
```

### Feature Injection Flow

```
User Enables Feature (Checkbox)
    ↓
enable_[feature]()
    ↓
Open Process (if not already open)
    ↓
Get Module Base Address
    ↓
Resolve Target Address
    ├─ Direct Offset → address = base + offset
    └─ Pattern Scan → find pattern in memory
    ↓
Allocate Memory
    ├─ Allocate near (relative JMP)
    └─ Or allocate anywhere (absolute JMP)
    ↓
Generate Shellcode
    ├─ Build machine code bytes
    └─ Calculate relative offsets
    ↓
Write to Memory
    ├─ Write code cave
    └─ Write injection patch
    ↓
log_info("Feature enabled")
    ↓
Store Injection Metadata
    ├─ inject_addr
    ├─ newmem_addr
    └─ original_bytes
```

---

## Configuration System

### Configuration Structure

```json
{
  "Language": "English (Default)",
  "ThemeColors": {
    "WindowBg": [50, 38, 65, 255],
    "Button": [175, 125, 195, 255],
    ...24 more colors
  },
  "DiscordClientID": "000",
  "FeatureStates": {
    "autosprint_enabled": false,
    "fullbright_enabled": false,
    ...
  }
}
```

### Configuration Operations

```python
load_config()      # Read from disk
save_config(data)  # Write to disk
init_config()      # Initialize defaults
get_config_path()  # Determine config location
```

---

## Threading Model

### Thread Management

**Main Thread**:
- UI rendering loop
- User interaction handling
- DOM updates

**Background Threads**:
```python
# Auto-refresh thread
auto_refresh_thread()
    └─ Monitors connection every 1 second

# Animation threads
animate_button_click()
animate_element_fade_in()

# Discord RPC thread
tray_icon.run()

# UI state update threads
Various callback threads
```

### Thread Safety

- Global variables protected by checksums
- Event-driven architecture
- Minimal shared state
- Thread-safe UI operations via DearPyGUI queue

---

## Error Handling

### Exception Handling Strategy

```
┌─────────────────────┐
│  Exception Thrown   │
└──────────┬──────────┘
           ↓
    ┌────────────────┐
    │ Catch block    │
    └────────┬───────┘
             ↓
    ┌─────────────────────┐
    │ Log error message   │
    │ to UI log display   │
    └─────────┬───────────┘
              ↓
    ┌────────────────────┐
    │ Cleanup state      │
    │ (disable feature)  │
    └────────┬───────────┘
             ↓
    ┌──────────────────┐
    │ Continue running │
    └──────────────────┘
```

### Key Exception Points

1. **Process Connection**
   - Target process not found
   - Insufficient privileges
   - Module not found

2. **Memory Operations**
   - Address read/write failures
   - Memory allocation failures
   - Pattern scan not found

3. **Injection Operation**
   - Shellcode too large
   - Relative offset out of range
   - Memory protection failures

---

## Dependencies

### External Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `pymem` | Latest | Process memory manipulation |
| `dearpygui` | Latest | UI framework |
| `pypresence` | Latest | Discord Rich Presence |
| `pyautogui` | Latest | Screen resolution detection |
| `psutil` | Latest | System utilities |
| `pillow` | Latest | Image handling (tray icon) |
| `pystray` | Latest | System tray integration |
| `requests` | Latest | HTTP requests |

### Standard Library Usage

```python
import ctypes           # Windows API calls
import struct           # Byte packing
import threading        # Multi-threading
import json             # Configuration
import random           # String generation
import time             # Delays & timing
import os, sys          # File/process paths
import webbrowser       # Link opening
```

### Windows API Integration

```python
kernel32 = ctypes.WinDLL('kernel32')

# Key WinAPI calls
- VirtualProtectEx()    → Memory protection
- CreateRemoteThread()  → Remote thread creation (if needed)
- FindWindowW()         → Window finding
- ShowWindow()          → Window visibility
```

---

## Initialization Sequence

```
1. Script Start
   └─ Check Admin Privileges

2. Load Configuration
   ├─ Read from JSON
   ├─ Load theme colors
   └─ Load language preference

3. Initialize Language
   └─ Set LANG_TEXTS dictionary

4. Create UI Context
   ├─ Initialize DearPyGUI
   ├─ Register fonts
   └─ Apply theme

5. Build UI Components
   ├─ Create windows
   ├─ Add buttons/sliders
   └─ Register callbacks

6. Start Background Threads
   ├─ Auto-refresh loop
   ├─ Discord RPC
   └─ Animation threads

7. Show UI
   └─ Start main event loop

8. Process Events
   └─ Handle user interactions until exit
```

---

## Shutdown Sequence

```
1. User Clicks "Self-Destruct"
   └─ Trigger graceful shutdown

2. Disable Active Features
   ├─ Restore original bytes
   ├─ Free allocated memory
   └─ Reset all injections

3. Stop Background Services
   ├─ Stop Discord RPC
   ├─ Stop auto-refresh
   └─ Stop animation threads

4. Cleanup Resources
   ├─ Close process handle
   ├─ Close tray icon
   └─ Flush logs

5. Exit Program
   └─ os._exit(0)
```

---

## Security Considerations

### Runtime Protection
- **Memory Validation**: Check addresses before write
- **Bounds Checking**: Validate offset ranges
- **Pattern Verification**: Confirm pattern matches expected bytes
- **Original Bytes**: Always save before modification

### Access Control
- **Admin Check**: Verify elevated privileges
- **Process Validation**: Confirm target process integrity
- **Protection Flags**: Use appropriate memory protection

### Audit Trail
- **Comprehensive Logging**: All operations logged
- **Timestamped Events**: When features enabled/disabled
- **Error Recording**: Stack traces on exceptions

---

## Performance Characteristics

### Memory Usage
- **Base**: ~50-100 MB (UI framework + libraries)
- **Per Injection**: ~20-50 KB (shellcode + allocation overhead)
- **Logs**: ~1-2 MB (rolling buffer)

### CPU Usage
- **Idle**: <1% (sleeping threads)
- **Active UI**: 2-5% (rendering + events)
- **During Injection**: Spike to 10% (brief operation)

### Latency
- **Reach Update**: <10ms (direct write)
- **Feature Toggle**: 50-500ms (injection + initialization)
- **Value Update**: <20ms (memory write)

---

## Extensibility

### Adding New Features

```python
def enable_new_feature():
    """Template for new feature implementation"""
    global pm, inject_addr_new, newmem_addr_new
    
    # 1. Validate state
    if inject_addr_new is not None:
        return
    
    # 2. Get target address
    inject_addr_new = module.lpBaseOfDll + 0xNEWOFFSET
    
    # 3. Allocate memory
    newmem_addr_new = allocate_near(inject_addr_new)
    
    # 4. Generate shellcode
    code = generate_shellcode(...)
    
    # 5. Do injection
    pm.write_bytes(newmem_addr_new, code, len(code))
    pm.write_bytes(inject_addr_new, patch, len(patch))
    
    log_info("New feature enabled")
```

### Plugin Architecture (Future)
- Dynamic feature loading
- User-defined offsets
- Custom shellcode templates

**Last Update**: March 11, 2026  
**Author**: iVyz3r_  
**License**: GPL-3.0  
**Status**: Production
