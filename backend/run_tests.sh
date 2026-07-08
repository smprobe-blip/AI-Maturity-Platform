#!/bin/bash
# Run all tests with coverage

set -e

echo "🧪 Running Backend Tests..."
echo "=========================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests
pytest tests/ \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    -v

echo ""
echo "✅ Tests completed!"
echo "📊 Coverage report: htmlcov/index.html"