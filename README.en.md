# CM Custom Instructions Plugin

**Version V1.3 | Updated: January 12, 2026**

---

## Language / 语言

- [English](README.en.md) | [中文简体](README.md)

---

## Overview

**CM (Custom Module)** is a user-defined custom instructions plugin that provides a series of practical custom instructions for Agilebot robots.

---

## Version Information

This plugin provides two versions, corresponding to different SDK versions:

### SDK v1.7.1.3 Version
- **Directory:** `CoordinateModifier（SDKV1.7.1.3）/`
- **Main File:** `CM_oldsdk.py`
- **Compatible SDK:** Python SDK v1.7.1.3
- **Compatible Robot Software Versions:**
  - Copper v7.6.X.X
  - Bronze v7.6.X.X

### SDK v2.0.0.0 Version
- **Directory:** `CoordinateModifier（SDKV2.0.0.0）/`
- **Main File:** `CM.py`
- **Compatible SDK:** Python SDK v2.0.0.0
- **Compatible Robot Software Versions:**
  - Copper v7.7.X.X
  - Bronze v7.7.X.X

### Version Selection Guide

- **Use SDK v1.7.1.3 version:** If your robot software version is v7.6.X.X
- **Use SDK v2.0.0.0 version:** If your robot software version is v7.7.X.X or higher

**Note:** Please select the corresponding plugin version based on your robot software version to ensure SDK version compatibility with the robot software version.

---

## Packaging Instructions

After plugin development is complete, you need to use the Agilebot plugin packaging tool for packaging. For detailed packaging and installation instructions, please refer to:

[📦 Packaging and Installation Documentation](https://dev.sh-agilebot.com/docs/extension/zh/02-development/04-package.html)

---

## Feature List

The plugin provides the following 11 custom instructions:

1. **SetTF** - Set tool coordinate system parameters (direct values)
2. **SetUF** - Set user coordinate system parameters (direct values)
3. **SetTF_R** - Read values from R register to set tool coordinate system parameters
4. **SetUF_R** - Read values from R register to set user coordinate system parameters
5. **SetTF_PR** - Read complete pose from PR register to set tool coordinate system
6. **SetUF_PR** - Read complete pose from PR register to set user coordinate system
7. **Incr** - R register increment
8. **Decr** - R register decrement
9. **Strp** - Parse string data to PR register
10. **TFShift** - Tool coordinate system compensation (based on vision feedback)
11. **DecToHex** - Convert from decimal to hexadecimal

---

## Detailed Instruction Documentation

### 1. SetTF - Set Tool Coordinate System Parameters (Direct Values)

Directly set specified parameters of the tool coordinate system through values.

**Parameters:**
- `ID` (int): Tool coordinate system ID number (1-30)
- `Pos` (int): Position parameter number (1-6)
  - 1: X coordinate (unit: mm)
  - 2: Y coordinate (unit: mm)
  - 3: Z coordinate (unit: mm)
  - 4: A angle (unit: degrees)
  - 5: B angle (unit: degrees)
  - 6: C angle (unit: degrees)
- `Value` (float): Parameter value

**Example:**
```
CALL_SERVICE CM, Set TF, ID=1, Pos=1, Value=111.11
```

---

### 2. SetUF - Set User Coordinate System Parameters (Direct Values)

Directly set specified parameters of the user coordinate system through values.

**Parameters:**
- `ID` (int): User coordinate system ID number (1-30)
- `Pos` (int): Position parameter number (1-6)
- `Value` (float): Parameter value

**Example:**
```
CALL_SERVICE CM, SetUF, ID=1, Pos=1, Value=222.354
```

---

### 3. SetTF_R - Read Values from R Register to Set Tool Coordinate System Parameters

Read values from the specified R register and set them to the specified parameters of the tool coordinate system.

**Parameters:**
- `ID` (int): Tool coordinate system ID number (1-30)
- `Pos` (int): Position parameter number (1-6)
- `R_ID` (int): R register number

**Example:**
```
CALL_SERVICE CM, Set TF_R, ID=3, Pos=1, R_ID=1
```

---

### 4. SetUF_R - Read Values from R Register to Set User Coordinate System Parameters

Read values from the specified R register and set them to the specified parameters of the user coordinate system.

**Parameters:**
- `ID` (int): User coordinate system ID number (1-30)
- `Pos` (int): Position parameter number (1-6)
- `R_ID` (int): R register number

**Example:**
```
CALL_SERVICE CM, SetUF_R, ID=3, Pos=1, R_ID=1
```

---

### 5. SetTF_PR - Read Complete Pose from PR Register to Set Tool Coordinate System

Read complete pose information (X, Y, Z, A, B, C) from the specified PR register and set it to the tool coordinate system at once.

**Parameters:**
- `ID` (int): Tool coordinate system ID number (1-30)
- `PR_ID` (int): PR register number

**Example:**
```
CALL_SERVICE CM, Set TF_PR, ID=2, PR_ID=1
```

---

### 6. SetUF_PR - Read Complete Pose from PR Register to Set User Coordinate System

Read complete pose information from the specified PR register and set it to the user coordinate system at once.

**Parameters:**
- `ID` (int): User coordinate system ID number (1-30)
- `PR_ID` (int): PR register number

**Example:**
```
CALL_SERVICE CM, SetUF_PR, ID=2, PR_ID=2
```

---

### 7. Incr - R Register Increment

Increase the value of the specified R register by the specified step size.

**Parameters:**
- `R_ID` (int): R register number
- `Step` (float): Increment step size, default is 1.0

**Example:**
```
CALL_SERVICE CM, Incr, R_ID=2, Step=1
```

---

### 8. Decr - R Register Decrement

Decrease the value of the specified R register by the specified step size.

**Parameters:**
- `R_ID` (int): R register number
- `Step` (float): Decrement step size, default is 1.0

**Example:**
```
CALL_SERVICE CM, Decr, R_ID=1, Step=1
```

---

### 9. Strp - Parse String Data to PR Register

Read string data from SR register, parse it, and write to PR register.

**Parameters:**
- `SR_ID` (int): String register number
- `R_ID_Status` (int): R register number for outputting material detection status (1=material present, 0=no material)
- `PR_ID` (int): PR register starting number
- `R_ID_Error` (int): R register number for outputting error status code (0=correct, 1=error)

**Data Format:**
- SR register format: Status bit, Data1, Data2, Data3,...
- Status bit: 0=no material, 1=material present
- Data mapping: Data1→PR X coordinate, Data2→PR Y coordinate, Data3→PR C angle
- Supported separators: comma, semicolon, vertical bar, tab, space, etc. (auto-detected)
- Each PR register stores 6 components (X, Y, Z, A, B, C), where Z, A, B retain original values

**Status Code Description:**
- `R_ID_Status`: Material detection status (1=material present, 0=no material)
- `R_ID_Error`: Error status code (0=correct, 1=error)
  - Status bit=0 (no material) → R_ID_Status=0, R_ID_Error=1 (error)
  - Status bit=1 and data format correct → R_ID_Status=1, R_ID_Error=0 (correct)
  - Status bit=1 but data format error → R_ID_Status=1, R_ID_Error=1 (format error)

**Example:**
```
SR[1] = "1,100.5,200.3,45.0"
// Description: Status bit=1 (material present), Data1=100.5 (X coordinate), Data2=200.3 (Y coordinate), Data3=45.0 (C angle)
// After execution: PR[1].x=100.5, PR[1].y=200.3, PR[1].c=45.0 (Z, A, B retain original values)
CALL_SERVICE CM, Strp, SR_ID=1, R_ID_Status=1, PR_ID=1, R_ID_Error=2
```

---

### 10. TFShift - Tool Coordinate System Compensation (Based on Vision Feedback Eye-to-Hand)

Calculate the relative deviation of the tool coordinate system by reading the deviation between different vision target points and the reference vision position, and output the deviation in the tool coordinate system.

**Parameters:**
- `InputTF_ID` (int): Reference calibration coordinate system number (1-30), default 1
- `ResultTF_ID` (int): Final coordinate system number after algorithm calculation (1-30), default 3
- `CamPose_ID` (int): Camera position PR register number, default 60
- `RefVis_ID` (int): Reference vision template data PR register number, default 61 (requires manual writing)
- `ActVis_ID` (int): Actual coordinate data PR register number output by vision, default 62 (requires manual writing)

**Example:**
```
// Assumptions:
// - TF[1] is the reference calibration coordinate system
// - PR[60] stores camera position pose
// - PR[61] stores reference vision template data (requires manual writing)
// - PR[62] stores actual vision coordinate data (requires manual writing)
// - TF[3] is the calculation result output coordinate system

CALL_SERVICE CM, TFShift, InputTF_ID=1, ResultTF_ID=3, CamPose_ID=60, RefVis_ID=61, ActVis_ID=62
```

**Working Principle:**
1. Read pose data of the reference tool coordinate system (InputTF_ID)
2. Read camera position pose (CamPose_ID) PR register data
3. Read reference vision template data (RefVis_ID) PR register data
4. Read actual vision coordinate data (ActVis_ID) PR register data
5. Calculate the relative deviation of the tool coordinate system through coordinate transformation matrix
6. Write calculation results to the result tool coordinate system (ResultTF_ID)

**Notes:**
- All PR registers must be manually created and written with correct pose data before use
- Reference vision template data (RefVis_ID) and actual vision coordinate data (ActVis_ID) need to be manually written to corresponding PR registers based on vision system output
- Calculation results will automatically undergo error verification and output error analysis information in logs
- Tool coordinate system ID must be between 1-30

---

### 11. DecToHex - Convert from Decimal to Hexadecimal

Convert decimal value in R register to hexadecimal string and write to SR register.

**Parameters:**
- `R_ID` (int): R register number containing the decimal number to convert (supports integers and floats)
- `SR_ID` (int): SR register number for saving the converted hexadecimal string

**Conversion Rules:**
1. Float handling: Truncation (directly discard decimal part, no rounding)
2. Value range: 32-bit integer (-2147483648 to 2147483647)
3. Negative number handling: Represented in 32-bit two's complement form
4. Output format: Fixed 8-digit hexadecimal string (uppercase, zero-padded to 8 digits)

**Example:**
```
// Example 1: Positive number conversion
R[1] = 255
CALL_SERVICE CM, DecToHex, R_ID=1, SR_ID=1
// Result: SR[1] = "000000FF"

// Example 2: Float truncation
R[1] = 255.99
CALL_SERVICE CM, DecToHex, R_ID=1, SR_ID=1
// Result: SR[1] = "000000FF" (truncated to 255)

// Example 3: Negative number conversion (32-bit two's complement)
R[1] = -1
CALL_SERVICE CM, DecToHex, R_ID=1, SR_ID=1
// Result: SR[1] = "FFFFFFFF"

// Example 4: Negative number conversion
R[1] = -255
CALL_SERVICE CM, DecToHex, R_ID=1, SR_ID=1
// Result: SR[1] = "FFFFFF01"

// Example 5: Zero value
R[1] = 0
CALL_SERVICE CM, DecToHex, R_ID=1, SR_ID=1
// Result: SR[1] = "00000000"
```

**Notes:**
- Floats in R register will be truncated to integers (no rounding)
- Values must be within 32-bit integer range (-2147483648 to 2147483647)
- Negative numbers are represented in 32-bit two's complement form
- Output is always an 8-digit uppercase hexadecimal string, zero-padded to 8 digits

---

## Key Features

### Core Features

- **Long Connection Mechanism:** Automatically manages robot connection, auto-connects on first call, reuses existing connection when already connected
- **Automatic Register Creation:** Strp instruction supports automatic R register creation (if not exists), PR registers require manual creation
- **Data Validation:** All instructions include complete parameter validation and error handling
- **Precision Control:** Coordinate system parameter values automatically retain three decimal places
- **Automatic Separator Detection:** Strp instruction supports automatic detection of multiple separators (comma, semicolon, vertical bar, tab, space, etc.)
- **Data Verification Mechanism:** Strp instruction immediately verifies data after writing to PR register

---

## Important Notes

### Important Tips

1. **Coordinate System ID Range:** ID must be between 1-30, 0 is the base coordinate system and cannot be modified
2. **Parameter Number:** Position parameter number must be between 1-6 (1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C)
3. **Register Existence:** Before using R register or PR register, it is recommended to ensure the register has been created (Strp instruction supports automatic R register creation)
4. **Connection Status:** Ensure the robot is correctly connected and accessible, the plugin will automatically manage connections
5. **Data Type:** All numeric parameters will automatically undergo type conversion and validation
6. **Strp Instruction Special Notes:**
   - PR registers require manual creation, please ensure PR registers exist before use
   - R_ID_Status and R_ID_Error registers will be automatically created if they don't exist
   - When status bit is 0, data parsing will not be performed, directly returns error (R_ID_Status=0, R_ID_Error=1)
   - After writing to PR register, data will be immediately verified for correct writing
   - It is recommended to check R_ID_Status and R_ID_Error values before use to determine execution results
7. **Error Handling:** All instructions return dictionary format, containing success, message/error fields, it is recommended to always check the success field

---

## Version History

### V1.3 (January 12, 2026)
- Added **DecToHex** instruction: Convert from decimal to hexadecimal
- Support converting decimal values in R register to 32-bit hexadecimal strings
- Support float truncation and negative number two's complement conversion
- Output fixed 8-digit uppercase hexadecimal format

### V1.2 (January 9, 2026)
- Added **TFShift** instruction: Tool coordinate system compensation (based on vision feedback)
- Support automatic calculation and update of tool coordinate system through vision feedback
- Provide high-precision coordinate transformation calculation with error verification support

### V1.1 (January 9, 2026)
- Added SDK v2.0.0.0 version support
- Updated coordinate system interface: Use `coordinate_system.TF/UF` subclasses
- Updated coordinate system data structure: Use `coordinate.data.x/y/z/a/b/c`
- Updated connection status check: `is_connect()` → `is_connected()`
- Updated error handling: Use `ret.errmsg` to get error information
- Updated Extension usage: Support independent instantiation to get IP address

---

**CM Custom Instructions Plugin | Version V1.3 | Updated: January 12, 2026 | © 2026**
