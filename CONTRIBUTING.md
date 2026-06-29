# Contributing to Smart Retry & Flaky Test Detector

Thank you for your interest in contributing to the Smart Retry & Flaky Test Detector framework!

## How to Contribute

### Reporting Issues
If you find a bug or have a feature request, please open an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/your-username/Smart-Retry-Flaky-Test-Detector.git

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/test_framework.py -v
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for all classes and functions
- Write unit tests for new features
- Keep functions small and focused

### Project Structure
- `core/` - Core framework components
- `ai/` - AI integration modules
- `pages/` - Page Object Model classes
- `tests/` - Test cases
- `utils/` - Utility functions
- `config/` - Configuration files

### Commit Messages
Use clear, descriptive commit messages:
- `feat: Add new feature`
- `fix: Fix bug in retry engine`
- `docs: Update README`
- `test: Add unit tests for flaky detector`

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
