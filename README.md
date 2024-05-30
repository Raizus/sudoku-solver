# Sudoku Variant Solver

A sudoku variant solver, using google's ortools library, and specifically it's cp-sat solver.

## Usage examples:

For help on how to use the tool type:

```
    psolver -h
```

To solve a single puzzle you can use

```
    psolver /path/to/puzzle_file.json
```

To solve multiple puzzles you can pass a folder or multiple paths to files

```
    psolver /path/to/puzzle_folder/
```

or

```
    psolver /path/to/puzzle_file_1.json ... /path/to/puzzle_file_n.json
```

You can also use arguments to log the solutions, change the maximum time before the solver stops or the maximum number of solutions before the solver stops:

```
    psolver /path/to/puzzle_file.json -l --max_time 360 --max_sols 40
```
