#!/usr/bin/env bash

set -x


if [ -z "${FORGEJO_WORKSPACE}" ];
then
    export FORGEJO_WORKSPACE=$(readlink -f "$(dirname $0)/..")
    export PYSRC=src
fi

if [ ! -e "${FORGEJO_WORKSPACE}/venv/bin/activate" ];
then
    python3 -m venv "${FORGEJO_WORKSPACE}/venv"
fi

source "${FORGEJO_WORKSPACE}/venv/bin/activate"

pip install -r "${FORGEJO_WORKSPACE}/tests/lint_requirements.txt"
mypy --install-types --non-interactive "${FORGEJO_WORKSPACE}/${PYSRC}"

mypy --disallow-untyped-defs "${FORGEJO_WORKSPACE}/${PYSRC}" || exit $?
flake8 --max-line-length 120 "${FORGEJO_WORKSPACE}/${PYSRC}" || exit $?
pydoclint --style sphinx -sfn true -csm true "${FORGEJO_WORKSPACE}/${PYSRC}" || exit $?
