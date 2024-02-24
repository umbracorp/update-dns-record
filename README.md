# Update DNS Records

A script to run that will update DNS records for a specified provider to a given ID, or detect the ID of the current machine.

## Installation

```bash
python -m venv .venv
. .venv/bin/activate
pip install .
```

## Usage

```bash
python -m update-dns-record --help
```

### Environment Variables

```env
API_KEY=abcdefghijk0123456789   # The API token for DNS provider auth
LOG_DIR=./logs                  # Directory to output logs to
```

## Docker

### Build

```bash
docker build -t update-dns-record .
```

### Run

```bash
docker run --rm --env-file .env update-dns-record --help
```
