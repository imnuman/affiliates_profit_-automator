# Contributing Guide

Thank you for considering contributing to the ClickBank Affiliate SaaS project!

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, browser, versions)

### Suggesting Enhancements

1. Check existing issues and discussions
2. Create an issue with:
   - Clear use case
   - Expected benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Ensure tests pass
6. Commit with conventional commits
7. Push to your fork
8. Open a Pull Request

## Development Setup

See [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) for detailed instructions.

## Coding Standards

### Python (Backend)

```python
# Use type hints
def get_user(user_id: str) -> User:
    ...

# Use docstrings
def calculate_commission(amount: Decimal) -> Decimal:
    """
    Calculate affiliate commission.

    Args:
        amount: Sale amount in dollars

    Returns:
        Commission amount in dollars
    """
    ...

# Follow PEP 8
# Use Black for formatting
# Use isort for import sorting
```

### TypeScript (Frontend)

```typescript
// Use interfaces for objects
interface User {
  id: string
  email: string
}

// Use functional components
const Component: React.FC<Props> = ({ prop }) => {
  return <div>{prop}</div>
}

// Use descriptive names
const handleSubmit = () => { ... }
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user profile page
fix: resolve authentication bug
docs: update API documentation
style: format code with prettier
refactor: simplify campaign logic
test: add tests for product search
chore: update dependencies
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_api/test_auth.py::test_login

# With coverage
pytest --cov=app tests/
```

### Frontend Tests

```bash
# Run tests
npm test

# Update snapshots
npm test -- -u
```

## Documentation

- Update relevant docs when making changes
- Add inline comments for complex logic
- Include examples in API documentation

## Review Process

1. Automated checks must pass (tests, linting)
2. At least one maintainer approval required
3. All conversations must be resolved
4. Branch must be up to date with main

## Questions?

- Open an issue for discussion
- Join our Discord community
- Email: dev@yourcompany.com
