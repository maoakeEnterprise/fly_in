SRC = src/__main__.py

UTILS = utils/flag_manager.py utils/parsing.py

MP_CACHE = .mypy_cache

P_CACHE = __pycache__

PT_CACHE = .pytest_cache

TESTS = tests/test_flag_manager.py

FLAG_T = tests/test_flag_manager.py

PARS_T = tests/test_parsing.py

.PHONY: install run norming norming_mp lint clean copy_data unzip_data test_flag_manager

install:
	uv sync

run:
	uv run python -m src --graph --launch_M1

test_flag_manager:
	PYTHONPATH=. uv run pytest $(FLAG_T)

test_parsing:
	PYTHONPATH=. uv run pytest $(PARS_T)

norming:
	watch uv run flake8 $(SRC) $(UTILS) $(TESTS)

norming_mp:
	watch uv run mypy $(SRC) $(UTILS) $(TESTS)

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