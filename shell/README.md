# Lab fork

## Ejecución de las pruebas

Las pruebas verifican el comportamiento de la shell implementada enviandole
comandos y leyendo la salida de los programas que ésta crea. En este sentido, el
prompt genera problemas al parsear la salida.

Por esta razón es necesario compilar la shell en **modo no interactivo**. Esto
quire decir que no se ve a imprimir el _prompt_ ni ningún mensaje de
error/debug.

La shell de la cátedra viene preparada para compilar la shell en modo no
interactivo. Para eso, limpiar los binarios generados y volver a compilar
definiendo la variable de entorno `TEST_SHELL`. El procedimiento sería entonces:

```
# En el directorio donde esté su shell
make clean
make -B -e SHELL_TEST=true
```

**IMPORTANTE**: esto compila la shell en modo no interactivo, al ejecutarlo
notarán la diferencia. Si quieren volver a la versión original sencillamente
vuelvan a compilar con `make clean; make`.

### Ejecución nativa

Para ejecutar las pruebas de forma nativa, es necesario instalar las
dependencias. Deben contar con una versión de `pyton3` instalda, junto con su
correspondiente `pip3` para poder instalar módulos de Python.

Las únicas dependencias para la ejecución son los módulos de python `[termcolor]` y `[pyyaml]`.

[termcolor]: https://pypi.org/project/termcolor/
[pyyaml]: https://pyyaml.org/

Para instalarla, alcanza con ejecutar:

```bash
pip install termcolor
```

Con las dependencias instaladas, correr las pruebas usando el target de Makefile
`test`. Es necesario definir, previamente, en una variable de entorno
(`TARGET_SHELL`) el path completo a su shell compilada en modo no interactivo.

Si la variable `TARGET_SHELL` no está definida correctamente, Makefile arrojará
un error:

```
$ make test
Makefile:8: *** Indique el path a una shell mediante la variable de entorno
TARGET_SHELL.  Stop.
```

Para definir la variable, sencillamente se puede agregar como variable temporal
para este comando; o bien ejecutar una única vez (por terminal) el built-in
_export_.

```
# Opción 1: indicar la shell en cada comando
TARGET_SHELL=/path/a/mi/shell make test

# Opción 2: definir la variable globalmente para la sesión actual
export TARGET_SHELL=/path/a/mi/shell
make test
```

#### Probar que las pruebas están andando

Como las pruebas validan el comportamiento de una shell normal, puede utilizarse
una shell pre-existente para validar que el entorno de pruebas funciona
correctamente.

Pueden utilizar `bash` para correr las pruebas.

```
$ TARGET_SHELL=/bin/bash make test
./test-shell.py /bin/bash /vagrant/labs/lab-tests/shell/reflector
Test temp files will be stored in /tmp/tmphjeojw7r-shell-test
PASS 1/23: Tests that cd . and cd .. works correctly by checking pwd (no prompt)
(./tests/cd_back.yaml)
PASS 2/23: Tests that cd works correctly by checking pwd (no prompt)
(./tests/cd_basic.yaml)
PASS 3/23: Tests that cd with no arguments takes you home (/proc/sys :D)
(./tests/cd_home.yaml)
PASS 4/23: Test that empty variables are not substituted
(./tests/env_empty_variable.yaml)
PASS 5/23: Test that large variables are substituted properly
(./tests/env_large_variable.yaml)
PASS 6/23: Test that magic variable $? works properly
(./tests/env_magic_variable.yaml)
PASS 7/23: Test simple variable substitution (./tests/env_substitution.yaml)
PASS 8/23: Test that unset variables are not substituted
(./tests/env_unset_variable.yaml)
PASS 9/23: Tests that child proceses exit if execve fails
(./tests/execve_exits_if_failed.yaml)
PASS 10/23: Test that consecutive pipes do not leak file descritors into the
executed command. (./tests/pipes_does_not_leak_fds.yaml)
PASS 11/23: Tests that the shell properly waits to the left child
(./tests/pipes_wait_left_child.yaml)
PASS 12/23: Tests that the shell properly waits to the right child
(./tests/pipes_wait_right_child.yaml)
PASS 13/23: Tests that redirecting stdin from a non-existing file does not
create an empty file. (./tests/redirect_does_not_create.yaml)
PASS 14/23: Test that redirects do not leak file descritors into the executed
command. (./tests/redirect_does_not_leak_fds.yaml)
PASS 15/23: Tests that a failed redirect prevents the command from executing
(./tests/redirect_dont_execve_if_failed.yaml)
PASS 16/23: Tests that redirecting stderr works as expected
(./tests/redirect_stderr.yaml)
PASS 17/23: Tests that stderr to stdout (2>&1) redirection works as expected
(./tests/redirect_stderr_to_stdout.yaml)
PASS 18/23: Tests that redirecting stdin works as expected
(./tests/redirect_stdin.yaml)
PASS 19/23: Tests that redirecting stdout works as expected
(./tests/redirect_stdout.yaml)
PASS 20/23: Tests that redirecting stdout works as expected
(./tests/redirect_stdout_trunc.yaml)
PASS 21/23: Test simple echo command (./tests/simple_echo.yaml)
PASS 22/23: Test simple env variable (./tests/simple_env.yaml)
PASS 23/23: Test exit built-in (./tests/simple_exit.yaml)
23 out of 23 tests passed
```

**DISCLAIMER**: estas pruebas están en versión beta y es posible que tengan
bugs/errores. Solo las probamos con `/bin/bash`, otras terminales podrían tener
fallas. Si encuentran un error, avisenos!

## Docker

También existe la posibilidad de utilizar [Docker](https://docs.docker.com/engine/install/) para correr las pruebas. Alcanza con ejecutar:

```bash
./run labpath
```
