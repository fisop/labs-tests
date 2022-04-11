# Lab fork

## Dependencias

- [ttp](https://ttp.readthedocs.io/en/latest/index.html)

Alcanza con ejecutar:

```bash
pip install ttp
```

## Ejecutar

Consultando la _ayuda_ disponible mediante el flag `-h` o `--help`, se obtiene:

```
usage: test-fork [-h] [-c {find,pingpong,xargs,primes}] labpath

Test runner for Lab Fork - FISOP

positional arguments:
  labpath               path to the lab under test

optional arguments:
  -h, --help            show this help message and exit
  -c {find,pingpong,xargs,primes}, --command {find,pingpong,xargs,primes}
                        command to be tested
```

## Docker

También existe la posibilidad de utilizar [Docker](https://docs.docker.com/engine/install/) para correr las pruebas. Alcanza con ejecutar:

```bash
./run labpath [-c {find,pingpong,xargs,primes}]
```
