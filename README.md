---
title: NBA Fantasy Game
emoji: 🏀
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.28.0
python_version: 3.11
app_file: app.py
pinned: false
license: mit
---

# NBA Fantasy Predictor

A modern Streamlit application that allows you to build a custom NBA fantasy team and compete against computer-generated opponents. The application uses a neural network model to predict game outcomes based on historical player statistics.

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

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Machine Learning**: [TensorFlow](https://www.tensorflow.org/) & [Keras](https://keras.io/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Data Storage**: Local CSV-based storage (`snowflake_nba.csv`)
- **Development Tools**: [uv](https://github.com/astral-sh/uv), [Pytest](https://pytest.org/), [Ruff](https://github.com/astral-sh/ruff), [Mypy](http://mypy-lang.org/)

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

This repository is licensed under the MIT License.
