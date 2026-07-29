UV ?= uv

.PHONY: help setup install install-notebooks install-dl lock format lint test validate docs check smoke generate-smoke-data

help: ## Показать доступные команды
	@awk 'BEGIN {FS = ":.*## "; print "Команды:"} /^[a-zA-Z_-]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Создать окружение и установить зависимости разработки
	$(UV) sync --group dev --extra cv

setup: install ## Совместимый псевдоним для первичной настройки

install-notebooks: ## Установить также инструменты Jupyter
	$(UV) sync --group dev --group notebooks --extra cv

install-dl: ## Установить CPU-профиль глубокого обучения
	$(UV) sync --group dev --group notebooks --extra cv --extra torch-cpu --extra deep-learning

lock: ## Обновить uv.lock из pyproject.toml
	$(UV) lock

format: ## Отформатировать Python-код
	$(UV) run --group dev ruff format coursekit scripts tests
	$(UV) run --group dev ruff check --fix coursekit scripts tests

lint: ## Проверить стиль и статические ошибки
	$(UV) run --group dev ruff format --check coursekit scripts tests
	$(UV) run --group dev ruff check coursekit scripts tests

test: ## Запустить модульные тесты
	$(UV) run --group dev pytest

validate: ## Проверить структуру репозитория и ноутбуки
	$(UV) run --group dev python scripts/validate_repository.py

docs: ## Проверить ссылки и строго собрать сайт курса
	$(UV) run python scripts/validate_markdown_links.py
	$(UV) run --group docs mkdocs build --strict

check: lint test validate docs ## Выполнить все быстрые проверки

smoke: ## Исполнить только ноутбуки с metadata.course_ci.smoke=true
	$(UV) run python scripts/smoke_open_pipeline.py
	$(UV) run --group notebooks --extra cv python scripts/smoke_notebooks.py

generate-smoke-data: ## Создать 48 синтетических изображений для быстрых опытов
	$(UV) run python scripts/generate_smoke_data.py
