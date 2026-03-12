# 🔍 Aegleseeker - Reverse Engineering Documentation

Complete guide to reverse engineering techniques, tools, and methodologies used to discover and validate Aegleseeker offsets and injection points.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Required Tools](#required-tools)
- [Core Techniques](#core-techniques)
- [Offset Discovery Process](#offset-discovery-process)
- [Pattern Analysis](#pattern-analysis)
- [Memory Scanning](#memory-scanning)
- [Shellcode Development](#shellcode-development)
- [Validation Methodology](#validation-methodology)
- [Common Challenges](#common-challenges)
- [Best Practices](#best-practices)
- [Tool Workflow](#tool-workflow)
- [Documentation Standards](#documentation-standards)

---

## Overview

### Purpose
Reverse engineering (R.E.) is the process of discovering memory addresses, patterns, and injection points in a target application through analysis of executable behavior and memory structure.

### Scope
This guide covers techniques for discovering Minecraft game modifications at runtime without source code access.

### Disclaimer
This documentation is for educational purposes only. Unauthorized modification of software may violate terms of service and applicable laws.

---

## Required Tools

### Essential Tools

#### 1. Cheat Engine
**Purpose**: Interactive memory scanning and pattern discovery  
**Key Features**:
- Hex value scanning
- Float/double searches
- Pattern scanning
- AOB (Array of Bytes) scanning
- Memory breakpoints
- Assembly inspection

**Download**: cheatengine.org

#### 2. x64dbg / x32dbg
**Purpose**: Low-level debugger for instruction analysis  
**Key Features**:
- Step-through execution
- Breakpoint setting
- Register inspection
- Memory dump analysis
- Call stack tracing

**Download**: x64dbg.com

#### 3. IDA Pro / Ghidra
**Purpose**: Static binary analysis and disassembly  
**Key Features**:
- Decompilation
- Function identification
- Cross-reference analysis
- Graph visualization
- Plugin support

**IDA**: idapro.com  
**Ghidra**: ghidra-sre.org (Free)

#### 4. Process Explorer / Process Monitor
**Purpose**: Process and system monitoring  
**Features**:
- Module enumeration
- Handle inspection
- DLL information

**Download**: Microsoft Sysinternals

### Optional Tools

- **HxD**: Hex editor for binary inspection
- **Frida**: Dynamic instrumentation framework
- **ApiMonitor**: API call tracing
- **WinDbg**: Windows kernel debugger

---

## Core Techniques

### 1. Static Analysis

Process of analyzing executable without running it.

#### Disassembly
```
Tool: IDA Pro / Ghidra
Process:
1. Load executable (.exe)
2. Analyze function entry points
3. Identify key functions
4. Document cross-references
5. Export symbols and locations
```

#### Binary Pattern Recognition
```
Look for:
- Function prologue/epilogue patterns
- Common instruction sequences
- Register allocation patterns
- Memory access patterns
```

### 2. Dynamic Analysis

Process of analyzing program behavior at runtime.

#### Breakpoint Analysis
```
1. Attach debugger to process
2. Set breakpoint at known location
3. Trigger game behavior
4. Step through instructions
5. Inspect register/memory values
6. Identify location modifications
```

#### Memory Tracing
```
Technique:
1. Take memory snapshot
2. Perform action (move closer to target)
3. Take second snapshot
4. Compare differences
5. Narrow down address range
6. Repeat until single address identified
```

### 3. Pattern Scanning

Automatic discovery of code sequences.

#### AOB (Array of Bytes) Scanning
```
Format: signature = b"\xF3\x0F\x10\x80\xA0\x01\x00\x00"

Process:
1. Identify byte sequence
2. Search in memory
3. Verify pattern matches
4. Calculate relative offset
5. Store for dynamic discovery
```

#### Wildcard Patterns
```
Pattern: F3 0F 10 80 A0 01 00 00
         ├─ F3 0F       = movss instruction
         ├─ 10 80       = memory read
         ├─ A0 01 00 00 = offset 0x1A0
         └─ Rest        = trailing bytes

With Wildcards:
F3 0F 10 80 ?? ?? ?? ?? = match any 4 bytes in offset
```

---

## Offset Discovery Process

### Methodology: Reach Control (0xB52A70)

**Goal**: Find memory address controlling player attack distance.

#### Step 1: Identify Mechanic
```
Game Mechanic: Player reach affects distance targets can be hit
Evidence: Attack damage falls off with distance
Range: ~3 blocks (default) to 15 blocks (modified)
```

#### Step 2: Initial Scanning

**Cheat Engine Process**:
```
1. Open Minecraft process in Cheat Engine
2. Start game, move to target area
3. Scan for reach value (default: 3.0 as float)
   - Value Type: Float
   - Scan Type: Exact Value
   - Value: 3.0

Result: Thousands of matches (filter needed)
```

#### Step 3: Narrow Results

**Constraint Method**:
```
1. Find new reach value > 3.0 (e.g., modify in game code)
2. Re-scan for NEW value
3. Results narrow significantly
4. Repeat: increase value, scan, narrow

Example progression:
Scan 3.0    → 9,000+ results
Scan 4.0    → 500 results
Scan 5.0    → 50 results
Scan 10.0   → 3 results
```

#### Step 4: Pattern Analysis

**Examine Memory Context**:
```
Cheat Engine Steps:
1. Right-click on candidate address
2. Select "Pointer scan for this address"
3. Analyze pointer chain
4. Identify base pointer (module base)
5. Calculate offset: address - base_address

Example:
Address found: 0x7FFF0000 + offset
Module base:  0x7FF00000
Offset:       0xB52A70
```

#### Step 5: Validation

**Verify Offset Discovery**:
```python
# In Aegleseeker
base = module.lpBaseOfDll
reach_address = base + 0xB52A70
value = pm.read_float(reach_address)

# Expected: ~3.0 or last modified value
assert 3.0 <= value <= 15.0, "Invalid reach address"
```

---

## Pattern Analysis

### Hitbox Control Pattern Discovery

#### Goal: Locate Hitbox Size Modification Point

#### Step 1: Function Identification

**Cheat Engine Breakdown Hit**:
```
1. Modify hitbox value (0.6 initial)
2. Take hit in game
3. Game calculates collision
4. Breakpoint on address modification
5. CPU window shows instruction:
   F3 0F 10 81 D0 00 00 00 = movss xmm0, [rcx+0xD0]
6. This loads hitbox from register offset 0xD0
```

#### Step 2: Pattern Extraction

```
Full Sequence Found:
Address: 0x00007FF0B4157B0
F3 0F 10 81 D0 00 00 00    movss xmm0, [rcx+0xD0]
C3                         retn
89 81 D0 00 00 00          mov [rcx+0xD0], eax

Pattern Identified:
└─ F3 0F 10 81 D0 00 00 00 (hitbox read)
└─ Offset 0xD0 is storage location
```

#### Step 3: Offset Extraction

```
Instruction: mov [rcx+0xD0], eax
Breakdown:
├─ 89 81 = mov r32, arg
├─ D0 00 00 00 = offset 0xD0 (little-endian)
└─ This modifies target+0xD0
```

#### Step 4: Signature Creation

```
Static Offset Method:
Injection Point: 0x4B57B0 (base + offset)
Storage Location: rcx + 0xD0

Signature Method (Fallback):
Pattern: F3 0F 10 81 D0 00 00 00
Scan module for this sequence
```

---

## Memory Scanning

### Scan Types in Cheat Engine

#### 1. Exact Value Scan
```
Use Case: Find specific numeric value
Example: Reach value = 3.0 (float)
Process:
- Enter exact value to search
- Rapidly narrow with repeated scans
```

#### 2. Increased/Decreased Value Scan
```
Use Case: Track changes over time
Example: Health decreases during damage
Process:
- Scan for "Decreased value"
- Get damaged
- Scan again
- Results narrow to health address
```

#### 3. Range Scan
```
Use Case: Find value within range
Example: Position between -100 and 100
Process:
- Specify min/max values
- Scan entire value range
- Multiple results returned
```

#### 4. Array of Bytes Scan
```
Use Case: Find known instruction sequence
Example: F3 0F 10 80 A0 01 00 00
Process:
- Convert assembly to hex bytes
- Search in memory
- Results point to instruction location
```

### Cheat Engine Scanning Tutorial

```python
# Equivalent in Python (for reference)

def scan_memory(pattern: bytes, address_range):
    """
    Scan memory for byte pattern
    """
    results = []
    for addr in address_range:
        if memory[addr:addr+len(pattern)] == pattern:
            results.append(addr)
    return results

# Usage
pattern = b"\xF3\x0F\x10\x80\xA0\x01\x00\x00"
hits = scan_memory(pattern, (0x7FF00000, 0x7FF50000))
print(f"Found {len(hits)} matches")
```

---

## Shellcode Development

### Shellcode Design Process

#### Goal: Create Hitbox Modification Shellcode

#### Step 1: Understand Original Code

```assembly
; Original instruction at 0x4B57B0
movss xmm0, [rcx+0xD0]    ; Load current hitbox value
; ... rest of function
```

#### Step 2: Design Modification

```
Objective: Override hitbox value before game uses it

Strategy:
1. Load custom value into register
2. Write to hitbox location
3. Execute original instruction (for safety)
4. Return to next instruction
```

#### Step 3: Write Assembly

```assembly
; Injected code (new memory location)
mov eax, 0x3F999999          ; Load 1.2 as float (0x3F999999)
mov [rcx+0xD0], eax          ; Write to hitbox location
movss xmm0, [rcx+0xD0]       ; Original instruction
jmp 0x4B57B8                 ; Jump back (inject_addr + 8)
```

#### Step 4: Assemble to Machine Code

```python
import struct

# mov eax, <value>
code = b"\xB8"                                      # MOV EAX imm32
code += struct.pack('<f', 1.2)                     # Value as float bytes

# mov [rcx+0xD0], eax  
code += b"\x89\x81\xD0\x00\x00\x00"               # MOV [rcx+disp], EAX

# movss xmm0, [rcx+0xD0]
code += b"\xF3\x0F\x10\x81\xD0\x00\x00\x00"       # MOVSS XMM0, [RCX+disp]

# jmp back
target = inject_addr + 8
rel_offset = target - (newmem_addr + len(code) + 5)
code += b"\xE9" + rel_offset.to_bytes(4, 'little', signed=True)  # JMP rel32
```

#### Step 5: Inject

```python
pm.write_bytes(newmem_addr, code, len(code))
# Create JMP at original location
jmp_rel = newmem_addr - (inject_addr + 5)
patch = b"\xE9" + jmp_rel.to_bytes(4, 'little', signed=True) + b"\x90" * 3
pm.write_bytes(inject_addr, patch, 8)
```

---

## Validation Methodology

### Verification Checklist

#### 1. Address Validation

```
Before Writing Memory:
☑ Address is within game module bounds
☑ Address is not in read-only section
☑ Original value matches expected type
☑ Address persists across game updates
```

#### 2. Pattern Verification

```
For Pattern-Scanned Offsets:
☑ Pattern search finds exactly one match
☑ Surrounding instructions make sense
☑ Pattern stable across game versions
☑ False positives ruled out
```

#### 3. Functional Testing

```
After Modification:
☑ Feature changes observed in game
☑ Change magnitude is expected
☑ No crashes or unexpected behavior
☑ Reversal/disable works properly
```

#### 4. Long-Term Validation

```
Continuous Monitoring:
☑ Offset persists across game restarts
☑ Offset stable through game updates
☑ No gradual degradation observed
☑ Documentation updated if changed
```

---

## Common Challenges

### Challenge 1: ASLR (Address Space Layout Randomization)

**Problem**: Base address changes every run

**Solution**:
```
Use Module Base + Offset Pattern:
- Discover offset relative to module
- At runtime: base = GetModuleHandle() + offset
- Provides dynamic addressing
```

**Testing**:
```
Restart game multiple times
Verify address changes but offset remains constant
```

### Challenge 2: Data Alignment

**Problem**: Float values may be misaligned

**Solution**:
```python
# Test different alignments
for offset in range(0, 0x10):
    addr = base + offset
    try:
        value = pm.read_float(addr)
        if 0.0 <= value <= 100.0:  # Expected range
            print(f"Found at offset: {hex(offset)}")
    except:
        pass
```

### Challenge 3: Multiple Candidates

**Problem**: Pattern matches multiple locations

**Solution**:
```
Create More Specific Pattern:
- Include unique surrounding bytes
- Use longer pattern (8+ bytes)
- Add context verification code
```

### Challenge 4: Encrypted/Obfuscated Code

**Problem**: Pattern changed between versions

**Solution**:
```
Fallback Mechanisms:
1. Try direct offset first
2. Fall back to pattern scan
3. Fall back to manual user input
4. Log all attempts for debugging
```

### Challenge 5: Anti-Cheat Detection

**Problem**: Some servers detect modifications

**Mitigation**:
```
Best Practices:
- Use pattern scanning (harder to detect)
- Restore original bytes on disable
- Minimize code footprint
- Only modify at specific locations
- Use stealthy injection techniques
```

---

## Best Practices

### 1. Documentation

**For Each Offset, Document**:
```
- Address: 0xB52A70
- Type: Float (4 bytes)
- Purpose: Player reach distance
- Range: 3.0 - 15.0
- Discovery Date: 2026-03-11
- Verified Until: Game version X.X.X
- Notes: May change with updates
```

### 2. Testing

**Create Test Cases**:
```
Test Case: Reach Modification
├─ Precondition: Game loaded, connected
├─ Action: Set reach to 5.0
├─ Expected: Player can hit from 5 blocks
├─ Verification: Damage falloff at 5 blocks
└─ Cleanup: Disable modification
```

### 3. Version Control

**Track Offsets Over Time**:
```
Version    Release Date    Reach Offset    Status
v1.1.71    2026-03-11     0xB52A70        Valid
v1.1.70    2026-03-10     0xB52A70        Valid
v1.1.69    2026-03-09     0xB52A50        Deprecated
```

### 4. Error Handling

**Graceful Degradation**:
```python
def get_offset_with_fallback():
    try:
        # Try direct offset
        return base + 0xB52A70
    except:
        try:
            # Try pattern scan
            return pattern_scan(module, pattern_bytes)
        except:
            # Fallback to manual
            log_error("Offset discovery failed")
            return None
```

### 5. Reverse Engineering Log

**Maintain Laboratory Notes**:
```
Date: 2026-03-11
Time: 14:30
Objective: Find reach address

Tools Used:
- Cheat Engine 7.4
- x64dbg

Process:
1. Scanned 3.0, got 9000 results
2. Increased reach in-game to 7.0
3. Scanned 7.0, got 50 results
4. Analyzed pointer chains
5. Found base + 0xB52A70

Verification:
- Tested 10 times, consistent
- Survives game restart
- Version: 1.1.71

Conclusion: VALID
```

---

## Tool Workflow

### Complete R.E. Session Example

#### Objective: Discover FullBright Offset

```
Hour 1: Initial Investigation
────────────────────────────
- Open Cheat Engine
- Attach to Minecraft process
- Explore module list
  └─ Note: Minecraft.Win10.DX11.exe base address
- Examine memory map
  └─ Identify game code section

Hour 2: Behavior Analysis
────────────────────────
- Trigger full brightness behavior
- Watch memory changes
- Set breakpoint on suspicious reads
- Analyze calling functions
- Examine assembly at breakpoint

Hour 3: Signature Hunting
──────────────────────────
- Extract instruction bytes
- Create pattern (with/without wildcards)
- Scan full module
- Verify single match
- Document offset

Hour 4: Validation
──────────────────
- Test modification works
- Test disable/restore works
- Verify pattern scanning
- Test multiple game restarts
- Create test case
```

### IDA Pro Workflow

```
1. Load Target
   - File → Open → Minecraft.Win10.DX11.exe
   - Wait for auto-analysis (~5-10 minutes)

2. Search for Function
   - Ctrl+F → Search for bytes or strings
   - Look for function prologues
   - Identify key functions

3. Analyze Imports
   - Look at imported functions
   - Trace calls to memory access functions
   - Follow cross-references

4. Document Findings
   - Add comments to assembly
   - Create custom segments for mods
   - Export address list

5. Verify in x64dbg
   - Transfer addresses to debugger
   - Set breakpoints
   - Watch behavior
```

---

## Documentation Standards

### Offset Documentation Template

```markdown
## [Feature Name] - Discovery Report

### Metadata
- **Offset**: 0xXXXXXXXX
- **Type**: [Float/Int/Byte/etc]
- **Size**: [4/8/16/etc] bytes
- **Module**: Minecraft.Win10.DX11.exe
- **Version**: 1.1.71
- **Date Discovered**: YYYY-MM-DD
- **Status**: [Valid/Deprecated/Unstable]

### Technical Details
- **Purpose**: [What does this value control?]
- **Value Range**: [Min - Max]
- **Default Value**: [Original game value]
- **Injection Type**: [Direct/Pattern/Script]

### Discovery Process
1. [Step 1]
2. [Step 2]
3. [Etc]

### Validation Results
- [Test case 1]: PASS
- [Test case 2]: PASS
- [Etc]

### Notes
[Any additional information]
```

### Pattern Documentation Template

```
Pattern Name: FullBright Brightness Read
────────────────────────────────────────

Hex Pattern:    F3 0F 10 80 A0 01 00 00
Assembly:       movss xmm0, [rax+0x1A0]
Bytes:          8
Wildcards:      None (unique signature)

Context:
- Located in rendering routine
- Loads brightness multiplier
- Called every frame

Usage:
pm.pattern_scan_module(
    b"\xF3\x0F\x10\x80\xA0\x01\x00\x00",
    module
)
```

---

## Advanced Topics

### Pointer Chain Analysis

```
Address Found: 0x7FF0B52A70
Pointer Chain: [base + 0x52A70] → [+0x20] → [+0x30]

Meaning:
1. Base of module
2. + 0x52A70 = pointer to object A
3. Object A + 0x20 = pointer to object B
4. Object B + 0x30 = actual reach value

Advantage: More stable across versions
```

### Multi-Version Support

```
Version Check:
- Detect game version at runtime
- Lookup offset from table
- Fall back to pattern scan if mismatch

Example:
offsets = {
    "1.1.71": 0xB52A70,
    "1.1.70": 0xB52A70,
    "1.1.69": 0xB52A50,
}

def get_offset(version):
    return offsets.get(version, pattern_scan())
```

### Anti-Tamper Verification

```python
def verify_injection_integrity():
    """Verify injected code not modified"""
    expected = original_bytes
    actual = pm.read_bytes(inject_address, len(expected))
    
    if expected != actual:
        log_error("Injection compromised!")
        disable_feature()
        return False
    return True
```

---

## Learning Resources

### Recommended Reading
1. "Practical Reverse Engineering" - Dang et al.
2. "The IDA Pro Book" - Eagle
3. "Windows x64 Assembly" - Various
4. Documentation on x64 calling conventions

### Online Resources
- Reverse Engineering Discord communities
- Assembly language tutorials
- Memory editing forums
- Tool documentation (CE, IDA, Ghidra)

### Practice Exercises
1. Find simple values in practice programs
2. Create POC (Proof of Concept) modifications
3. Analyze small game mods
4. Document findings in markdown
5. Build tools to automate discovery

---

## Conclusion

Reverse engineering is both art and science. Success requires:

✓ **Technical Knowledge**: Assembly, memory models, OS internals  
✓ **Patience**: Systematic analysis, careful documentation  
✓ **Creativity**: Problem-solving, pattern recognition  
✓ **Discipline**: Version control, testing, safety checks  
✓ **Ethics**: Respect ToS, legal, responsible disclosure  

Document everything. Share knowledge responsibly. Stay curious.

---

**Last Update**: March 11, 2026  
**Author**: iVyz3r_  
**License**: GPL-3.0  
**Status**: Educational Reference
