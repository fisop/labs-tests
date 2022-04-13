TARGET_SHELL ?=
REFLECTOR ?= $(abspath ./reflector)

all: reflector

compile-target-shell: check-env
	$(MAKE) -C $(TARGET_SHELL) clean
	$(MAKE) -C $(TARGET_SHELL) 

test: check-env reflector compile-target-shell
	./test-shell.py $(TARGET_SHELL) $(REFLECTOR)

check-env:
ifndef TARGET_SHELL
	$(error Indique el path a una shell mediante la variable de entorno TARGET_SHELL)
endif

clean:
	rm reflector

.PHONY: all clean compile-target-shell test

