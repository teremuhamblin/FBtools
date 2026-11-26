PY ?= python

.PHONY: help install lint format typecheck test check docs build clean docker

help: ## Affiche cette aide
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Installe le projet en mode développement + hooks
	$(PY) -m pip install -e ".[dev,docs]"
	pre-commit install

lint: ## Analyse statique (Ruff)
	ruff check src tests

format: ## Formate le code
	ruff format src tests
	ruff check --fix src tests

typecheck: ## Vérification de types (mypy strict)
	mypy

test: ## Tests + couverture
	pytest --cov --cov-report=term-missing

check: lint typecheck test ## Tout vérifier (comme la CI)
	ruff format --check src tests

docs: ## Sert la documentation en local
	mkdocs serve

build: clean ## Construit wheel + sdist
	$(PY) -m build
	twine check dist/*

docker: ## Construit l'image Docker
	docker build -t fbtools:local .

clean: ## Supprime les artefacts
	rm -rf build dist site .coverage coverage.xml htmlcov .pytest_cache .ruff_cache .mypy_cache
