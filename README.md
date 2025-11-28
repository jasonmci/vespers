# vespers

A Textual-based terminal user interface application.

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/jasonmci/vespers.git
   cd vespers
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

To start the Vespers application:

```bash
python src/main.py
```

Press `q` to quit the application.

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

Format code with Black:
```bash
black src/ tests/
```

Sort imports with isort:
```bash
isort src/ tests/ --profile black
```

### Linting

Check formatting:
```bash
black --check src/ tests/
isort --check-only src/ tests/ --profile black
```

## CI/CD

The project uses GitHub Actions for continuous integration. On every push and pull request:
- Code formatting is checked (Black, isort)
- Tests are run with pytest
