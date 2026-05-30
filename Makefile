SRC = src/__main__.py

MP_CACHE = .mypy_cache

P_CACHE = __pycache__

PT_CACHE = .pytest_cache

PARS_T = tests/test_parsing.py

.PHONY: install run norming norming_mp lint clean copy_data unzip_data

install:
	uv sync

run:
	uv run python -m src --launch_M1

test_parsing:
	PYTHONPATH=. uv run pytest tests/test_parsing.py

norming:
	watch uv run flake8 $(SRC)

norming_mp:
	watch uv run mypy $(SRC)

lint:
	uv run flake8 . --exclude=./.venv
	uv run mypy . --exclude "\.venv" --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf $(MP_CACHE) */$(MP_CACHE) */$(P_CACHE) $(PT_CACHE)

debug:
	uv run python -m pdb $(SRC)

copy_data:
	cp ~/Downloads/maps.tar.gz .

unzip_data:
	tar -xvf *.tar.gz maps