TARGET_SHELL_DIR ?=

ifdef TARGET_SHELL_DIR
TARGET_SHELL = $(TARGET_SHELL_DIR)/sh
endif

TARGET_SHELL ?=
REFLECTOR ?= $(abspath ./reflector)

all: reflector

compile-target-shell: check-env
	$(MAKE) -C $(TARGET_SHELL_DIR) clean
	$(MAKE) -C $(TARGET_SHELL_DIR) -B -e SHELL_TEST=true

test: check-env reflector
ifdef TARGET_SHELL_DIR
test: compile-target-shell
endif
	./test-shell.py $(TARGET_SHELL) $(REFLECTOR)

check-env:
ifndef TARGET_SHELL
	$(error Indique el path a una shell mediante la variable de entorno TARGET_SHELL)
endif

clean:
	rm reflector

.PHONY: all clean compile-target-shell test

