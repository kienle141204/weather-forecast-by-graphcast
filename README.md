# Weather Forecast using GraphCast

This project uses the GraphCast model to make weather forecasts for Hanoi, Vietnam.

## Prerequisites

- Docker and Docker Compose installed on your system
- CDS API key from Copernicus Climate Data Store

## Setup

1. Create a `config` directory in the project root:
```bash
mkdir config
```

2. Create a file `config/key_cds.txt` with your CDS API key:
```
CDS_API_KEY=your_api_key_here
```

3. Create an `output` directory for the results:
```bash
mkdir output
```

## Running the Application

### Using Docker Compose (Recommended)

1. Build and run the container:
```bash
docker-compose up --build
```

### Using Docker directly

1. Build the Docker image:
```bash
docker build -t weather-forecast .
```

2. Run the container:
```bash
docker run -v $(pwd)/config:/app/config -v $(pwd)/output:/app/output -e CDS_API_KEY=your_api_key_here weather-forecast
```

## Output

The application will generate two CSV files in the `output` directory:
- `inputs_hanoi_{day}.csv`: Contains the input data used for prediction
- `predictions_hanoi_{day}.csv`: Contains the weather predictions

## Project Structure

- `main.py`: Main entry point of the application
- `extract.py`: Functions for extracting data from CDS
- `transform.py`: Functions for transforming and preparing data
- `model.py`: GraphCast model implementation
- `utils.py`: Utility functions
- `constants.py`: Constants and configuration
- `requirements.txt`: Python dependencies
- `Dockerfile`: Docker configuration
- `docker-compose.yml`: Docker Compose configuration
- `.dockerignore`: Files to exclude from Docker build 