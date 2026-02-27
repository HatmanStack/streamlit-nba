# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-27

### Added
- **Foundation Model**: Highlighted the complete Keras/TensorFlow foundation model setup trained on 2018 NBA data.
- **Apache 2.0 License**: Officially transitioned the project to the Apache 2.0 license.
- **Modernized README**: Added tech stack badges and improved project documentation.
- **Hugging Face Deployment**: Prepared the repository for deployment to Hugging Face Spaces.

### Changed
- **Data Layer**: Transitioned from a remote database to a local CSV-based data source (`snowflake_nba.csv`) using Pandas.
- **Game Logic**: Optimized away team generation and implemented session state persistence to prevent infinite loops.
- **UI Improvements**: Refined the team builder logic and added debug logging for better maintenance.

### Fixed
- Team saving logic in the Streamlit interface.
- Import sorting and type annotations to satisfy CI requirements.
- Path resolution for the Keras model in different environments.

## [1.0.0] - 2026-02-20

### Added
- Initial release of the NBA Fantasy Predictor.
- Streamlit multi-page application.
- Keras-based game winner prediction model.
- Basic team builder and box score simulator.
