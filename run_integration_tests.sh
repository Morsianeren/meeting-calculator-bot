#!/bin/bash

# This script runs the integration tests with real email credentials
# Make sure config/.env exists with the correct credentials

echo "Running integration tests with real email credentials"
echo "These tests will connect to actual email servers..."

python -m pytest tests/test_email_integration.py -v -m integration
