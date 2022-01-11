[![Python application](https://github.com/jbchouinard/untitled-word-game/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/jbchouinard/untitled-word-game/actions/workflows/python-app.yml)

# Untitled Word Game

![Screenshot of the game](screenshot.png?raw=true "Untitled Word Game")

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
