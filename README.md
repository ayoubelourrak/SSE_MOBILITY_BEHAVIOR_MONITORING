# Mobility Behavior Monitoring System

## System Architecture

The system consists of 8 interconnected microservices:

1. **Input System** - Simulates sensor data input from smart shoes
2. **Ingestion System** - Collects and validates incoming sensor data
3. **Preparation System** - Preprocesses and cleans raw sensor data
4. **Segregation System** - Splits data into training/testing sets with balancing
5. **Development System** - Trains and validates machine learning classifiers
6. **Production System** - Deploys trained models for real-time classification
7. **Evaluation System** - Monitors classifier performance and accuracy
8. **Orchestrator System** - Starts the entire workflow

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Python 3.11+** (for local development)

## Quick Start

### 1. Start the System
```bash
docker compose up
```

### 2. Stop the System
```bash
docker compose down
```

## Detailed Setup

### Environment Configuration

The system can be configured through environment variables in `docker-compose.yaml`:

#### Input System
- `SITUATION`: Set to `"ideal"` or `"real"` to control data generation mode

#### Ingestion System
- `OPERATIVE_MODE`: Set to `"development"` or `"production"`
- `EVALUATION`: Set to `1` for evaluation phase, `0` otherwise

#### Development System
- `LAYER_RANGE`: Neural network hidden layer range (e.g., `"1,3"`)
- `NEURON_RANGE`: Neurons per layer range (e.g., `"4,128"`)
- `NO_STOP`: Set to `1` for automated mode, `0` for interactive

#### Production System
- `EVALUATION_PHASE`: Set to `1` to enable evaluation mode
- `CLASSIFIER_DEPLOYED`: Set to `1` when classifier is ready

### Data Volumes

The system requires external data directories for persistent storage:

```
../Data/
├── input/data/logs/           # Input system logs
├── segregation/data/          # Balancing and coverage reports
├── development/data/          # Trained classifiers and reports
├── classifier/                # Production classifiers
└── evaluation/data/reports/   # Evaluation reports
```

## Usage Guide

### Development Mode Workflow

1. **Data Generation**: Input system generates synthetic sensor data
2. **Data Ingestion**: Raw sensor data is collected and validated
3. **Data Preparation**: Missing samples are interpolated, features extracted
4. **Data Segregation**: Training/testing sets created with proper balancing
5. **Model Development**: Multiple classifiers trained and validated
6. **Model Selection**: Best performing classifier selected based on validation metrics

### Production Mode Workflow

1. **Real-time Classification**: Production system receives prepared sensor sessions
2. **Label Generation**: Trained classifier predicts mobility behavior
3. **Performance Monitoring**: Evaluation system tracks accuracy and errors