# Sysmonify

Real-time system resource monitoring.

# Development

Create virtual environment

```bash
python3 -m venv venv
```

Activate virtual environment

```bash
pip install -r dev-requirements.txt
```

Run development sever

```bash
cd sysmonify
daphne -b 0.0.0.0 -p 8000 sysmonify.asgi:application
```

# Testing

TODO

# Design Notes
