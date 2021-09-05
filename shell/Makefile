TARGET_SHELL ?= /bin/bash
REFLECTOR ?= $(abspath ./reflector)

all: reflector

test: reflector
	./test-shell.py $(TARGET_SHELL) $(REFLECTOR)

clean:
	rm reflector

.PHONY: all clean test

