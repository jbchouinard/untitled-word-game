default: venv/bin/word-game

venv:
	python -m venv venv
	venv/bin/pip install cython pyinstaller

wordgame/fastcheck.c: venv
	venv/bin/python setup.py build_ext --inplace

venv/bin/word-game: venv wordgame/fastcheck.c
	venv/bin/pip install .

dist/word-game: venv wordgame/fastcheck.c
	venv/bin/pyinstaller -F --windowed word-game.py

clean:
	rm -f wordgame/fastcheck.c wordgame/fastcheck.*.so *.spec
	rm -rf build dist venv __pycache__ wordgame/__pycache__ wordgame.egg-info

.PHONY: clean default
