## Simple makefile for common dev tasks

.PHONY: build up down test backend-install frontend-install

build:
	docker compose build

up:
	docker compose up --build

down:
	docker compose down

backend-install:
	python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r backend/requirements.txt

frontend-install:
t	cd react-frontend && npm ci

test:
	pytest -q
