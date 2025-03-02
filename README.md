# Sysmonify

Real-time system resource monitoring for Linux Desktops.

# Development

Create virtual environment

```bash
python3 -m venv venv
```

Activate virtual environment

```bash
source ./venv/bin/activate
```

```bash
pip install -r dev-requirements.txt
```

Collect Static files

```bash
cd sysmonify
python3 manage.py collectstatic
```

Run development sever

```bash
daphne -b 0.0.0.0 -p 8000 sysmonify.asgi:application
```

# Testing

Create virtual environment

```bash
python3 -m venv venv
```

Activate virtual environment

```bash
pip install -r dev-requirements.txt
```

Run unit tests

```bash
cd sysmonify
python3 manage.py test
```

# Project Roadmap

| Version | Release Date | Details |
|---------|--------------|---------|
| 0.0.1-alpha | 28-02-2025 | Initial Release: <br> &nbsp;&nbsp; - Django backend. <br> &nbsp;&nbsp; - Basic monitoring functionality for all major system resources. <br> &nbsp;&nbsp; - Websockets for updating UI in real-time. <br> &nbsp;&nbsp; - Web frontend (vanilla JS and Bootstrap). <br> &nbsp;&nbsp; - Base CI/CD for automated testing.
| 0.0.2-alpha | 31-03-2025 | Improved reliability and performance of existing functionality.
| 0.1.0-beta | 30-04-2025 | Additional Features: <br> &nbsp;&nbsp; - User Settings (SQLite). <br> &nbsp;&nbsp; - UI Light/Dark modes <br> &nbsp;&nbsp; - General visual improvements to UI
| 0.2.0-beta | 30-05-2025 | Gnome overlay
