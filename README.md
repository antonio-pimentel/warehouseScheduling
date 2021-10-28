# Warehouse Packaging Scheduling

## 1st Project - ALC 2021/2022

- António Pimentel, 86385

## Usage

```bash
python3 proj1.py < [input-file.wps]
```

The tool reads the problem instance from the standard input. \
And writes the solution to the standard output.

## Tool Description

This tool is implemented in python and uses the PySAT toolkit.

The optimal solution for each problem instance is found by doing multiple calls to a SAT solver (Glucose4) in a linear search starting at a upper bound for the timespan and decreasing it until the request is not satisfiable.

### Variables Used

The problem was modeled using variables to represent, at each timestep, whether or not:

- a runner is in a given position
- a product was placed on the conveyor belt
- a product arrived to the packing station
- a runner is active
