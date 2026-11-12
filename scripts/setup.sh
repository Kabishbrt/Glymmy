#!/bin/bash
set -e

echo "Glymmy — First-Time Setup"
echo "=========================="

if [ ! -f .env ]; then
  echo "Creating .env from template..."
  cp .env.example .env
fi

if [ ! -f notebooks/datasets/mimic_labevents.csv ]; then
  echo "⚠ Warning: MIMIC-IV demo data not found at notebooks/datasets/"
  echo "  Download: wget -P notebooks/datasets https://physionet.org/files/mimic-iv-demo/2.2/hosp/labevents.csv.gz"
fi

if [ ! -f notebooks/datasets/GlucoBench/raw_data/dubosson.csv ]; then
  echo "⚠ Warning: GlucoBench data not found"
  echo "  Clone: cd notebooks/datasets && git clone https://github.com/IrinaStatsLab/GlucoBench.git"
fi

echo ""
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for Ollama to be ready..."
sleep 6

echo ""
echo "Pulling Gemma 4 E4B (this may take a few minutes)..."
docker exec glymmy-ollama ollama pull gemma4:e4b || echo "(model pull skipped — can be done later with 'make pull-models')"

echo ""
echo "✓ Setup complete!"
echo ""
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API docs:  http://localhost:8000/docs"
