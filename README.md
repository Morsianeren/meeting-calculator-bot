# Meeting Calculator Bot

## Overview
A Python bot that processes meeting invitations, estimates meeting costs, collects feedback, and stores data for analysis.

## Setup
1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `config/.env`.
4. Run the bot: `python main.py`

## Architecture
- **src/**: Source code, organized by modules (email, db, feedback, utils)
- **config/**: Configuration files and templates
- **tests/**: Unit and integration tests
- **doc/**: Documentation and design diagrams

## Usage
- Handles meeting invites from @deif.com
- Calculates cost using CSV lookups
- Sends feedback surveys and aggregates responses
- Stores meeting and feedback data in SQLite

## Deployment
- Docker support included (see Dockerfile)

## Contributing
- See code style and linting guidelines
- Run tests with `pytest`
