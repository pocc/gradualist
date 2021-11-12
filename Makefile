# Simple makefile to do simple tasks
.PHONY: all test clean

clean:
	rm temp*
test:
	python3 tests/test_code_fences.py
