# Caching Proxy Server

A simple caching proxy server built with FastAPI that forwards requests to an origin server and caches responses locally.

## Features

- Forwards GET requests to a configurable origin server
- Caches responses locally to reduce load on the origin
- Cache hit/miss headers (`X-Cache`)
- Clear cache option

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Start the proxy server:

```bash
python main.py --port 3000 --origin https://api.example.com
```

Clear the cache:

```bash
python main.py --clear-cache
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--port` | Port to run the proxy server on |
| `--origin` | Origin URL to forward requests to |
| `--clear-cache` | Clear the cached responses |
