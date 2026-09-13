PYTHON := $(shell python3 --version >/dev/null 2>&1 && echo python3 || echo python)
HEURISTICS := manhattan misplaced linear_conflict
PUZZLES := $(wildcard puzzles/*.txt)

.PHONY: all clean fclean re test run heuristics $(HEURISTICS) $(PUZZLES)

all:
	@echo "Usage:"
	@echo "  make puzzles/3x3.txt                solve with default heuristic"
	@echo "  make puzzles/3x3.txt manhattan     solve with a specific heuristic"
	@echo "  make heuristics puzzles/3x3.txt    compare the 3 heuristics (stats only)"
	@echo "  make run ARGS=\"-g 4\"               generate and solve a random puzzle"
	@echo "  make run ARGS=\"-f puzzles/3x3.txt -a greedy\""
	@echo "  make test / make clean / make fclean / make re"

# --- make puzzles/<file>.txt [<heuristic>] ---
$(PUZZLES):
	@if printf '%s\n' $(MAKECMDGOALS) | grep -qx heuristics; then exit 0; fi; \
	h=$$(printf '%s\n' $(MAKECMDGOALS) | grep -Ex 'manhattan|misplaced|linear_conflict' | head -1); \
	if [ -n "$$h" ]; then \
		$(PYTHON) -m src.main -f $@ -H $$h; \
	else \
		$(PYTHON) -m src.main -f $@; \
	fi

# --- flag goals used as: make puzzles/<file>.txt <heuristic> ---
$(HEURISTICS):
	@if ! printf '%s\n' $(MAKECMDGOALS) | grep -qx 'puzzles/[^ ]*\.txt'; then \
		echo "Usage: make puzzles/<file>.txt $@" >&2; \
		exit 1; \
	fi

# --- make heuristics puzzles/<file>.txt [...more files] ---
heuristics:
	@files=$$(printf '%s\n' $(MAKECMDGOALS) | grep -Ex 'puzzles/[^ ]*\.txt'); \
	if [ -z "$$files" ]; then \
		echo "Usage: make heuristics puzzles/<file>.txt" >&2; \
		exit 1; \
	fi; \
	for file in $$files; do \
		echo "== $$file =="; \
		for h in $(HEURISTICS); do \
			$(PYTHON) -m src.main -f $$file -H $$h -q; \
		done; \
	done

run:
	$(PYTHON) -m src.main $(ARGS)

test:
	@if $(PYTHON) -c "import pytest" >/dev/null 2>&1; then \
		$(PYTHON) -m pytest tests/ -v; \
	else \
		echo "pytest not installed, using unittest instead"; \
		$(PYTHON) -m unittest discover -s tests -v; \
	fi

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

fclean: clean

re: fclean all
