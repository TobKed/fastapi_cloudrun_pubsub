SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
# .DELETE_ON_ERROR:
MAKEFLAGS = --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

py = $$(if [ -d $(PWD)/'.venv' ]; then echo $(PWD)/".venv/bin/python3"; else echo "python3"; fi)
pip = $(py) -m pip

# Override PWD so that it's always based on the location of the file and **NOT**
# based on where the shell is when calling `make`. This is useful if `make`
# is called like `make -C <some path>`
PWD := $(realpath $(dir $(abspath $(firstword $(MAKEFILE_LIST)))))
MAKEFILE_PWD := $(CURDIR)
WORKTREE_ROOT := $(shell git rev-parse --show-toplevel 2> /dev/null)


.DEFAULT_GOAL := help


SRC_DIR = src
DOCKER_COMPOSE_SERVICE_WORKER = worker

.PHONY: help
help: ## Show this help
	@echo "Usage: make [target], targets are:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: setup-dev
setup-dev: ## setup dev environment: poetry, pre-commit
	pip install poetry==1.6
	poetry install
	pre-commit install 2>&1
	[ ! -e ".env" ] && cp ".env.example" ".env" || echo "file .env already exists"

.PHONY: gcloud-auth
gcloud-auth: ## Authenticate with gcloud
	gcloud auth application-default login

.PHONY: pre-commit
pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

.PHONY: update-pre-commit
update-pre-commit: ## Update pre-commit hooks
	pre-commit autoupdate

.PHONY: run
run: ## Run docker-compose in detached mode
	docker-compose -f docker-compose.yaml -f docker-compose.gcp-default-credentials.yaml up --detach

.PHONY: stop
stop: ## Stop docker-compose
	docker-compose down

.PHONY: build
build: purge ## Build docker-compose from scratch
	docker-compose build

.PHONY: purge
purge: ## Purge docker-compose
	docker-compose down --remove-orphans

.PHONY: logs
logs: ## Show docker-compose logs
	docker-compose logs --timestamps --follow

.PHONY: test
test: ## Run pytest
	docker-compose run --rm $(DOCKER_COMPOSE_SERVICE_WORKER) pytest ${args}

.PHONY: test-verbose
test-verbose: ## Run pytest with verbose output
	docker-compose run --rm $(DOCKER_COMPOSE_SERVICE_WORKER) pytest -s -x -vv --pdb ${args}
