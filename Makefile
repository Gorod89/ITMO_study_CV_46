UV ?= uv

.PHONY: help setup install install-notebooks install-dl install-retrieval install-inference install-yolo lock format lint test validate docs check smoke smoke-notebooks smoke-notebook generate-smoke-data

help: ## Показать доступные команды
	@awk 'BEGIN {FS = ":.*## "; print "Команды:"} /^[a-zA-Z_-]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Создать окружение и установить зависимости разработки
	$(UV) sync --group dev --extra cv

setup: install ## Совместимый псевдоним для первичной настройки

install-notebooks: ## Установить также инструменты Jupyter
	$(UV) sync --group dev --group notebooks --extra cv

install-dl: ## Установить CPU-профиль глубокого обучения
	$(UV) sync --group dev --group notebooks --extra cv --extra torch-cpu --extra deep-learning

install-retrieval: ## Добавить FAISS к CPU-профилю глубокого обучения
	$(UV) sync --group dev --group notebooks --extra cv --extra torch-cpu --extra deep-learning --extra retrieval

install-inference: ## Добавить ONNX Runtime к CPU-профилю глубокого обучения
	$(UV) sync --group dev --group notebooks --extra cv --extra torch-cpu --extra deep-learning --extra inference

install-yolo: ## Установить изолированный CPU-профиль Ultralytics YOLO
	$(UV) sync --group dev --group notebooks --extra torch-cpu --extra yolo

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

smoke: ## Проверить open pipeline и все отмеченные CPU smoke-ноутбуки
	$(UV) run python scripts/smoke_open_pipeline.py
	$(UV) run --group notebooks --extra cv python scripts/smoke_notebooks.py

smoke-notebooks: ## Исполнить все ноутбуки с metadata.course_ci.smoke=true
	$(UV) run --group notebooks --extra cv python scripts/smoke_notebooks.py

smoke-notebook: ## Исполнить один ноутбук: make smoke-notebook NOTEBOOK="путь.ipynb"
	@test -n "$(NOTEBOOK)" || (echo 'ОШИБКА: укажите NOTEBOOK="путь.ipynb"' >&2; exit 2)
	$(UV) run --no-sync python scripts/smoke_notebooks.py "$(NOTEBOOK)"

generate-smoke-data: ## Создать 48 синтетических изображений для быстрых опытов
	$(UV) run python scripts/generate_smoke_data.py
