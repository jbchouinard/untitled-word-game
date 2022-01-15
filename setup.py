from setuptools import setup, find_packages

try:
    from Cython.Build import cythonize

    ext_modules = cythonize("wordgame/fastcheck.pyx")
except ImportError:
    print("cython not found, will use slow check function")
    ext_modules = []

setup(
    name="untitled-word-game",
    version="3.0.0",
    url="https://github.com/jbchouinard/untitled-word-game.git",
    author="Jerome Boisvert-Chouinard",
    author_email="me@jbchouinard.net",
    description="Word game and solver.",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "word-game = wordgame.gui:main",
            "word-solver-benchmark = wordgame.solver:main",
        ]
    },
    ext_modules=ext_modules,
)
