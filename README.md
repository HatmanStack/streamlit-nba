---
title: NBA Fantasy Predictor
emoji: 🏀
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.28.0
python_version: 3.11
app_file: app.py
pinned: false
license: apache-2.0
---

# NBA Fantasy Predictor

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=flat&logo=TensorFlow&logoColor=white)
![Keras](https://img.shields.io/badge/Keras-%23D00000.svg?style=flat&logo=Keras&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=flat&logo=numpy&logoColor=white)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

A modern Streamlit application that allows you to build a custom NBA fantasy team and compete against computer-generated opponents. The application uses a neural network model to predict game outcomes based on historical player statistics.

## 🔗 Live App
Play the game [here](https://hatman-nba-fantasy-game.hf.space).

## 🚀 Features

- **Multi-page Interface**: Organized navigation between the home page, team builder, and game simulator.
- **Advanced Team Builder**:
    - Search for players from a comprehensive database of historical NBA stats.
    - Input validation for secure and accurate player searches.
    - Build a 5-player roster with real-time preview.
- **Dynamic Opponents**: Choose from multiple difficulty levels to generate challenging computer teams.
- **Foundation Model Architecture**: 
    - A complete neural network setup trained on the 2018 NBA season data.
    - Implemented using Keras/TensorFlow with a focus on reproducibility and extensibility.
    - Despite the focused dataset, it demonstrates a full ML lifecycle: data preprocessing, hyperparameter optimization, and deployment.
- **ML-Powered Predictions**: 
    - Predicts win probability and outcomes based on the combined stats of both starting lineups.
    - Utilizes automated hyperparameter tuning via `RandomizedSearchCV`.
- **Game Simulation**: Generates dynamic quarter-by-quarter box scores based on model predictions.
- **Clean Architecture**: Modular codebase with clear separation of concerns (ML, database, validation, and state management).

## 📋 Project Structure

```text
├── app.py              # Main entry point
├── pages/              # Streamlit page modules
├── src/                # Core application logic
│   ├── database/       # Data access and queries
│   ├── ml/             # Model loading and prediction
│   ├── models/         # Data models and schemas
│   ├── state/          # Session state management
│   ├── utils/          # UI and helper utilities
│   └── validation/     # Input validation logic
├── tests/              # Comprehensive test suite
├── scripts/            # Training and utility scripts
└── winner.keras        # Pre-trained prediction model
```

## ⚙️ Usage

### Quick Start with uv (Recommended)

```bash
# Install dependencies and run the app
uv run streamlit run app.py
```

### Standard Installation

```bash
# Install requirements
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 🧪 Development

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src
```

### Linting and Type Checking
```bash
# Run Ruff for linting and formatting
ruff check .

# Run Mypy for static type checking
mypy .
```

### Training the Model
The project includes a comprehensive training pipeline to rebuild the model from scratch using the 2018 NBA season results:
```bash
python scripts/compile_model.py
```
This script performs an automated search for the best architecture and hyperparameters (optimizers, initializers, etc.) before saving the final `winner.keras` model.

## 📄 License

This repository is licensed under the Apache License 2.0.
