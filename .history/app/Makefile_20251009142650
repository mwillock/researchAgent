PY:= python3
VENV:= .venv
PIP:= $(VENV)/bin/pip
UVICORN:= $(VENV)/bin/uvicorn
PYTEST:= $(VENV)/bin/pytest

APP_MODULE := app.main:app
HOST ?= $(APP_HOST)
PORT ?= $(APP_PORT)

#Default host and target incase not avaliable in env
HOST ?=
PORT ?=

#Phony targets
.PHONY: help setuup install hooks, fmt, lint, type, run , dev
