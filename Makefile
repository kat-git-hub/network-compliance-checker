.PHONY: help up down run test test-cov lint report clean all

help:
	@echo "Available commands:"
	@echo "  make up        - Start all containers"
	@echo "  make down      - Stop all containers"
	@echo "  make run       - Run Ansible compliance check"
	@echo "  make test      - Run pytest tests"
	@echo "  make test-cov  - Run tests with coverage report"
	@echo "  make lint      - Run ansible-lint"
	@echo "  make report    - Open HTML report in browser"
	@echo "  make all       - up + run + test"
	@echo "  make clean     - Stop containers and remove reports"

up:
	docker compose up -d

down:
	docker compose down

run:
	poetry run ansible-playbook -i hosts.ini site.yml

test:
	poetry run pytest tests/ -v

test-cov:
	poetry run pytest tests/ -v --cov=tests --cov-report=term-missing --cov-report=html:reports/coverage

lint:
	poetry run ansible-lint roles/

report:
	open reports/report.html

cov-report:
	open reports/coverage/index.html

all: up
	@echo "Waiting for SSH..."
	@sleep 40
	$(MAKE) run
	$(MAKE) test

clean:
	docker compose down
	rm -rf reports/*.html reports/*.json reports/coverage
