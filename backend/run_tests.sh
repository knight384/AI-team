#!/bin/bash

# Script to run tests with coverage
# Usage: ./run_tests.sh

set -e

echo "=== Running Auth API Tests ==="
echo ""

# Change to backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Clean up old test databases
echo "Cleaning up old test databases..."
rm -f test_auth.db *.db

# Run tests with coverage
echo ""
echo "Running tests with coverage..."
pytest app/tests/test_auth.py \
    --cov=app/routers/auth \
    --cov=app/models \
    --cov=app/security \
    --cov=app/schemas \
    --cov-report=term-missing \
    --cov-report=html \
    -v

# Display coverage summary
echo ""
echo "=== Coverage Summary ==="
echo "HTML report generated in: htmlcov/index.html"
echo ""

# Check if coverage meets requirement (80%)
coverage_percentage=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
if [ -z "$coverage_percentage" ]; then
    coverage_percentage=$(pytest --cov=app --cov-report=term app/tests/test_auth.py 2>&1 | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
fi

echo "Total coverage: ${coverage_percentage}%"

if [ ! -z "$coverage_percentage" ]; then
    if (( $(echo "$coverage_percentage >= 80" | bc -l) )); then
        echo "✓ Coverage meets requirement (≥80%)"
    else
        echo "✗ Coverage below requirement (${coverage_percentage}% < 80%)"
        exit 1
    fi
fi

echo ""
echo "=== All tests passed! ==="
