# Simple makefile to do simple tasks
.PHONY: all test clean

clean:
	Test*

test:
	python3 tests/test_code_fences.py