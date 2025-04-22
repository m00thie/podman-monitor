# Podman Monitor

A simple web application to monitor Podman containers.

## Features

- Web interface to view running Podman containers
- Real-time updates of container status
- Simple and lightweight

## Requirements

- Python 3.9+
- Poetry for dependency management
- Podman with socket enabled

## Installation

### Using Poetry

```bash
# Install dependencies
poetry install

# Run the application
poetry run python app.py
```

### Using Docker/Podman

```bash
# Build the image
podman build -t podman-monitor .

# Run the container
podman run -d --name podman-monitor -p 5000:5000 -v /run/podman/podman.sock:/run/podman/podman.sock:ro podman-monitor
```

## Configuration

Configuration is done through environment variables:

- `PODMAN_SOCKET`: Path to the Podman socket (default: `unix:///run/podman/podman.sock`)

## Usage

Once running, open your browser and navigate to:

```
http://localhost:5000
```

## License

MIT
