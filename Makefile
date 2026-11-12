.PHONY: help up down dev logs build clean pull-models backend frontend mobile test setup

help:
	@echo "Glymmy — AI Health Platform"
	@echo ""
	@echo "Commands:"
	@echo "  make setup        First-time setup (copies .env, builds, pulls Gemma 4)"
	@echo "  make up           Start all services"
	@echo "  make down         Stop all services"
	@echo "  make logs         Tail logs from all services"
	@echo "  make build        Rebuild all containers"
	@echo "  make clean        Stop services and remove volumes"
	@echo "  make pull-models  Pull Gemma 4 model into Ollama"
	@echo "  make backend      Run backend locally (no Docker)"
	@echo "  make frontend     Run frontend locally (no Docker)"
	@echo "  make mobile       Run Expo mobile app locally"

setup:
	@if [ ! -f .env ]; then cp .env.example .env && echo "✓ Created .env from template"; fi
	docker-compose build
	docker-compose up -d
	@echo ""
	@echo "Waiting for Ollama to be ready..."
	@sleep 6
	@$(MAKE) pull-models
	@echo ""
	@echo "✓ Glymmy is running:"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API docs:  http://localhost:8000/docs"

up:
	docker-compose up -d
	@echo "Frontend: http://localhost:3000  |  Backend: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build --no-cache

clean:
	docker-compose down -v
	@echo "✓ Cleaned containers and volumes"

pull-models:
	@echo "Pulling Gemma 4 E4B into Ollama (this may take a few minutes)..."
	docker exec glymmy-ollama ollama pull gemma4:e4b || true
	@echo "✓ Model ready"

backend:
	cd glymmy_backend && .venv/bin/python main.py

frontend:
	cd glymmy_frontend && npm run dev

mobile:
	cd glymmy_mobile && npm run dev
