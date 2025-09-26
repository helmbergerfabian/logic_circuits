# Logic Circuits (Pygame)

A simple graphical logic circuit editor and simulator built with **Pygame** and **NumPy**.  
You can place gates, wire them together, and generate truth tables.

## Features
- Drag & drop logic gates (AND, NOT, SysIN, SysOUT)
- Connect gates with wires
- Interactive add/remove ports
- Compute and display truth tables

## Installation
Clone the repo and create the environment:

```bash
git clone https://github.com/yourusername/logic-circuits.git
cd logic-circuits
conda env create -f environment.yml
conda activate logic-circuits
pip install -e .