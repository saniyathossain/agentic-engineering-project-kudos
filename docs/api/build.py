#!/usr/bin/env python3
"""Regenerates everything under docs/api (and docs/configuration.md) from the data modules.

    python3 docs/api/build.py

Sources of truth: endpoints.py (OpenAPI data), cases.py (client collections), envvars.py (configuration reference).
Needs only the Python 3 standard library.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

import gen_clients  # noqa: E402
import gen_docs  # noqa: E402
import gen_openapi  # noqa: E402


def main():
    doc = gen_openapi.write(HERE)
    gen_clients.write_all(HERE)
    gen_docs.write(HERE, doc)
    print("wrote openapi.yaml/json, postman/, insomnia/, bruno/, README.md, ../configuration.md")


if __name__ == "__main__":
    main()
