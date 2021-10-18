# Tents and trees solver

I played way too much of "Tents and trees" a mobile game from the play store that i started
to wonder if i couldn't make a solver for it.

This repository contains all the necessary code to solve a given problem.
I will explain how the usage of the code works however it is up to the reader to figure out how it works.


### About the game

You can find it easily on the android play store under the tame "Tents and trees".
It represents basically a $N \times N$ grid that contains, let's say $T_r$ trees.

For each tree exactly one tent must be placed adjacent to each tree.
Each row and column have a constraint associated to them which is the maximum number of tents that can be placed
in the corresponding row or column.


### Input format

The input format is:

```txt
[0-n]{n_columns}
[0-n]{n_rows}
([e|t][0-n] )*
([e|t][0-n] )*
...
([e|t][0-n] )*
```

* First two lines of the file describe the constraints for each col / row.
* $n_{columns}$ being the number of columns
* $n_{rows}$ being the number of rows
* The regular expression is used to described a single row of the board and is repeated $n_{rows}$ times

**/!\**: Some example files are given describing some boards under the `input/` directory, these are useful for understanding the syntax.

### Usage of the code

To run the code with a particular input file is very simple :

```sh
> python3 main.py [input_file_path]
```

This will print the initial read grid, then the time it took to solve it and the solved version.

Have fun using it!
