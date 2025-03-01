# Computer-Architecture

## Overview
This repository contains coursework projects that focus on understanding the fundamentals of CPU architecture, instruction decoding, caching mechanisms, and pipeline simulation.

## Projects

### 1) Instruction Decoder
- Extracts specific bits from 32-bit MIPS instructions.
- Supports both R-format and I-format instructions.
- Demonstrates instruction decoding using bit masking and shifting.

**Folder**: [`Project-1`](./Project-1)  
**Main file**: [`instruction_decoder.py`](./Project-1/instruction_decoder.py)  

### 2) Cache Simulator
- Simulates a direct-mapped cache with 16 slots.
- Implements cache read, write, and display operations.
- Uses write-back policy to update main memory.

**Folder**: [`Project-2`](./Project-2)  
**Main file**: [`cache.py`](./Project-2/cache.py)  

### 3) Pipeline Simulation
- Simulates a five-stage instruction pipeline (IF, ID, EX, MEM, WB).
- Implements register forwarding and hazard detection.
- Displays all pipeline register states at each clock cycle.

**Folder**: [`Project-3`](./Project-3)  
**Main file**: [`pipeline_simulator.py`](./Project-3/pipeline_simulator.py)
