# Word Game and Solver

Word guessing game and solver.

## Installation

### Optional - compile fastcheck

If Cython is installed, the fastcheck.pyx module can be compiled, which makes the
solver about 10 times faster.

```bash
pip install cython
python setup.py build_ext --inplace
```

### Install package

```bash
pip install .
```

## Usage

Play game:

```bash
word-game
```

Run solver benchmark:

```bash
word-solver-benchmark [best|good|fast]
```

## Strategy

The solver greedily maximizes the expected number of potential solutions
eliminated by the next guess, it is not the optimal strategy.
