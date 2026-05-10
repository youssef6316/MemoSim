# Memory Allocation Simulator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A graphical simulation tool for **memory allocation and deallocation using segmentation**, supporting **First-Fit** and **Best-Fit** dynamic storage-allocation algorithms.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Test Cases](#test-cases)
- [Tech Stack](#tech-stack)
- [Documentation](#documentation)
- [Building an Executable](#building-an-executable)
- [Author](#author)

---

## Overview

This project simulates how an operating system manages physical memory using **segmentation**. Unlike paging (fixed-size blocks), segmentation treats a program as a collection of logical segments—such as **Code**, **Data**, and **Stack**—each with its own size. The simulator visualizes the memory layout after every allocation and deallocation, making abstract OS concepts tangible.

The tool implements two classic allocation strategies:
- **First-Fit** – allocates the first hole that is large enough.
- **Best-Fit** – allocates the smallest hole that is large enough.

It also demonstrates **external fragmentation**, **hole coalescing**, and **atomic allocation** (all-or-nothing process loading).

---

## Features

- **Segmentation-based memory model** with variable-length segments
- **First-Fit & Best-Fit** allocation algorithms (switchable at runtime)
- **Atomic allocation** – a process is loaded only if **all** its segments fit
- **Automatic hole coalescing** after deallocation
- **Live memory canvas** – colored vertical bar showing allocated segments (amber) and free holes (charcoal)
- **Segment tables** – displays base/limit for every allocated process
- **Free & Allocated partition tables** – real-time hole and block tracking
- **Operation history log** – color-coded event log
- **Dark-themed modern UI** built with Tkinter

---

## Installation

### Prerequisites
- Python **3.8+** installed on your system
- No external pip packages required (uses only built-in `tkinter`)

### Clone & Run
```bash
# Clone or extract the project
cd memory_allocation_project

# Run the application
python main.py
```

---

## Usage

1. **Initialize Memory**
   - Enter the **Total Memory Size** (e.g., `1000`).
   - Define initial **holes** as comma-separated `start,size` pairs (one per line).
   - Click **Initialize Memory**.

2. **Select Allocation Method**
   - Choose **First-Fit** or **Best-Fit**.
   - Click **Set Method**.

3. **Add a Process**
   - Enter a **Process Name** (e.g., `P1`).
   - Enter segments in `name:size` format (e.g., `Code:100`).
   - Click **Add Process**.

4. **Allocate**
   - With the process name in the field, click **Allocate**.
   - The canvas and tables update instantly.

5. **Deallocate**
   - Select a process from the **Deallocation** dropdown.
   - Click **Deallocate**.
   - Freed segments become holes and merge with neighbors automatically.

---

## Project Structure

```
memory_allocation_project/
├── main.py                  # Application entry point
├── README.md
├── dist/
│   └── MemoryAllocator.exe
├── Controller/
│   ├── __init__.py
│   ├── models.py            # Data classes: Segment, Process, Hole, AllocatedBlock
│   └── memory_manager.py    # Core logic: allocation, deallocation, coalescing
├── UI/
│   ├── __init__.py
│   └── main_app.py          # Tkinter GUI with dark theme and memory canvas
└── Docs/
    ├── Project_Description.pdf
    ├── Test Cases.pdf
    └── Project_Documentation.pdf
```

---

## Test Cases

### Instructor Test Case

**Initial Setup:** Total = 1000K; Holes: (0,300), (400,250), (700,200)

| Step | Operation | First-Fit Result | Best-Fit Result |
|:---|:---|:---|:---|
| 1 | Allocate P1 (100,120,90) | ✅ Success | ✅ Success |
| 2 | Allocate P2 (200,40) | ✅ Success | ✅ Success |
| 3 | Allocate P3 (120,50) | ❌ Fail | ✅ Success |
| 4 | Deallocate P1 | ✅ Success | ✅ Success |
| 5 | Allocate P4 (230,40) | ✅ Success | ❌ Fail |

### Extra Verification Tests

| # | Test | Purpose |
|:---|:---|:---|
| 1 | **Exact Fit & Coalescing** | Verify holes return to original positions after exact-fit allocation and deallocation |
| 2 | **Best-Fit Fragmentation** | Confirm Best-Fit leaves the smallest possible fragment |
| 3 | **Atomic Allocation** | Ensure 3 segments into 2 holes fails with **zero** partial allocation |
| 4 | **Progressive Merging** | Deallocate middle, left, then right neighbors; verify merge into single (0,1000) hole |

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| Language | Python 3.8+ |
| GUI Framework | Tkinter (built-in) |
| Architecture | MVC-inspired (Controller / UI separation) |
| Packaging | PyInstaller (for `.exe` generation) |

---

## Documentation

- **[Project_Guide.html](Project_Guide.html)** – Comprehensive guide covering theory, architecture, design decisions, and test case analysis.
- **[EXE_Build_Guide.html](EXE_Build_Guide.html)** – Instructions for building a standalone Windows executable using PyInstaller.
- **[Project_Documentation.docx](Project_Documentation.docx)** – Formal submission document with tables, discussion, and screenshot placeholders.

---

## Building an Executable

To create a standalone `.exe` for Windows:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "MemoryAllocator" main.py
```

The executable will be generated in the `dist/` folder.

> ⚠️ If you encounter `ModuleNotFoundError`, ensure `__init__.py` files exist in both `Controller/` and `UI/` packages, or add `--paths "Controller" --paths "UI"` to the command.

---

## Author

**Youssef Yacoub**   
Course: CSE 335s – Operating Systems  
Date: May 2026

---

## License

This project is submitted as academic coursework. All rights reserved.