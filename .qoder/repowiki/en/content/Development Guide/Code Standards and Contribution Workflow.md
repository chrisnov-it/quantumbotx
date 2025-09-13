# Code Standards and Contribution Workflow

<cite>
**Referenced Files in This Document**   
- [requirements.txt](file://requirements.txt)
- [eslint.config.mjs](file://eslint.config.mjs)
- [package.json](file://package.json)
- [core/bots/controller.py](file://core/bots/controller.py)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py)
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py)
- [core/mt5/trade.py](file://core/mt5/trade.py)
</cite>

## Table of Contents
1. [Python Coding Standards and Linting](#python-coding-standards-and-linting)
2. [JavaScript Linting Rules](#javascript-linting-rules)
3. [Contribution Workflow](#contribution-workflow)
4. [Code Documentation and Type Hints](#code-documentation-and-type-hints)
5. [Code Review Checklist](#code-review-checklist)
6. [Testing and Linting Execution](#testing-and-linting-execution)
7. [Dependency Management](#dependency-management)
8. [Backward Compatibility and Core Modifications](#backward-compatibility-and-core-modifications)
9. [Unit Testing Guidelines](#unit-testing-guidelines)

## Python Coding Standards and Linting

The quantumbotx project adheres to PEP 8 guidelines for Python code style. While no explicit linting tool (e.g., flake8, pylint) is currently configured in the repository, the codebase demonstrates consistent formatting practices. The `requirements.txt` file lists core dependencies but does not include any linting packages, indicating that linting may be managed externally or is not currently enforced via automated tools.

Key PEP 8 compliance observations:
- Proper use of whitespace around operators and after commas
- Consistent indentation using 4 spaces
- Descriptive variable and function names using snake_case
- Appropriate line length (generally under 79 characters)
- Use of docstrings for function documentation

Example of properly formatted Python code from `controller.py`:
```python
def mulai_bot(bot_id: int):
    """
    Start a thread for the selected bot.
    """
    if bot_id in active_bots and active_bots[bot_id].is_alive():
        return True, f"Bot {bot_id} already running."

    bot_data = queries.get_bot_by_id(bot_id)
    if not bot_data:
        return False, f"Bot with ID {bot_id} not found."
```

**Section sources**
- [requirements.txt](file://requirements.txt)
- [core/bots/controller.py](file://core/bots/controller.py#L0-L176)

## JavaScript Linting Rules

Frontend JavaScript code consistency is enforced through ESLint, configured in `eslint.config.mjs`. The configuration follows modern ESLint module syntax using `defineConfig` and extends the recommended rules from `@eslint/js`. The setup ensures code quality across JavaScript, JSON, Markdown, and CSS files.

Key linting rules and configurations:
- Files with extensions `.js`, `.mjs`, `.cjs` are analyzed
- Browser globals are enabled, with additional custom globals like `Chart` marked as readonly
- CommonJS module format is specified for `.js` files
- Separate configurations for JSON, Markdown, and CSS files with their respective recommended rules

The `package.json` file confirms ESLint as a devDependency, ensuring consistent tooling across development environments.

```javascript
// Example of ESLint configuration from eslint.config.mjs
export default defineConfig([
  { 
    files: ["**/*.{js,mjs,cjs}"], 
    plugins: { js }, 
    extends: ["js/recommended"], 
    languageOptions: { 
        globals: {
            ...globals.browser,
            "Chart": "readonly"
        } 
    } 
  },
  { files: ["**/*.js"], languageOptions: { sourceType: "commonjs" } }
]);
```

**Section sources**
- [eslint.config.mjs](file://eslint.config.mjs#L0-L28)
- [package.json](file://package.json#L0-L10)

## Contribution Workflow

The contribution process for the quantumbotx project follows standard Git workflow practices:

1. **Fork the Repository**: Create a personal fork of the main repository
2. **Create a Branch**: Make a new branch for each feature or bug fix
3. **Implement Changes**: Write code following the project's style guidelines
4. **Run Tests and Linters**: Execute local tests and linting before submission
5. **Commit Changes**: Use descriptive commit messages following conventional patterns
6. **Push to Fork**: Push the branch to your forked repository
7. **Submit Pull Request**: Create a pull request to the main repository

The workflow emphasizes small, focused changes that are easier to review and integrate. Contributors should ensure their code does not break existing functionality, particularly in core components.

**Section sources**
- [package.json](file://package.json#L0-L10)
- [requirements.txt](file://requirements.txt)

## Code Documentation and Type Hints

The codebase demonstrates strong documentation practices with comprehensive docstrings and type hints. Functions include detailed descriptions of purpose, parameters, and return values. Type hints are used consistently to improve code clarity and enable better IDE support.

Example from `controller.py` showing proper documentation:
```python
def mulai_bot(bot_id: int):
    """Memulai thread untuk bot yang dipilih."""
    # Function implementation
```

The `trading_bot.py` file shows extensive use of type hints in class initialization:
```python
def __init__(self, id, name, market, risk_percent, sl_pips, tp_pips, timeframe, 
             check_interval, strategy, strategy_params={}, status='Dijeda'):
```

Docstrings should follow the project's existing pattern, providing clear explanations of function behavior, parameters, and return values. Type hints should be included for all function parameters and return values where possible.

**Section sources**
- [core/bots/controller.py](file://core/bots/controller.py#L0-L176)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L0-L169)

## Code Review Checklist

All pull requests should be evaluated against the following criteria:

**Functionality**
- Does the code achieve its intended purpose?
- Are edge cases and error conditions properly handled?
- Does it integrate correctly with existing components?

**Performance**
- Are there any unnecessary computations or database queries?
- Is data processing efficient for expected data volumes?
- Are external API calls minimized and properly cached when appropriate?

**Security**
- Are user inputs properly validated?
- Are there any potential injection vulnerabilities?
- Is sensitive data handled securely?

**Maintainability**
- Is the code well-structured and readable?
- Are functions appropriately sized and focused?
- Is error handling consistent and informative?
- Are logging statements appropriate and useful for debugging?

**Backward Compatibility**
- Does the change preserve existing API contracts?
- Are database schema changes handled with migration scripts?
- Are configuration options maintained for existing deployments?

**Section sources**
- [core/bots/controller.py](file://core/bots/controller.py#L0-L176)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L0-L169)

## Testing and Linting Execution

Before submitting code, contributors must run all relevant tests and linting tools locally:

**Python Testing**
- Run unit tests for modified components
- Verify integration with dependent modules
- Test error handling scenarios

**JavaScript Linting**
- Execute ESLint using the configured rules:
```bash
npx eslint "**/*.js"
```

**Frontend Testing**
- Test JavaScript functionality in supported browsers
- Verify UI interactions and state management
- Check console for any errors or warnings

The absence of explicit test scripts in `package.json` suggests that testing may be handled through separate Python test runners for backend code and manual or browser-based testing for frontend components.

**Section sources**
- [package.json](file://package.json#L0-L10)
- [eslint.config.mjs](file://eslint.config.mjs#L0-L28)

## Dependency Management

Dependencies are managed through two primary files:

**Backend (Python)**
- `requirements.txt`: Specifies pinned versions of Python packages
- Current dependencies include Flask, MetaTrader5, pandas, numpy, and related data analysis packages
- All versions are explicitly pinned for reproducible environments

**Frontend (JavaScript)**
- `package.json`: Defines devDependencies for development tools
- Includes ESLint and related plugins for code quality enforcement
- Uses modern ESLint plugin architecture with separate packages for JSON, Markdown, and CSS linting

Example from `requirements.txt`:
```
Flask==3.1.1
MetaTrader5==5.0.5120
pandas==2.3.1
numpy==1.23.5
```

Example from `package.json`:
```json
{
  "devDependencies": {
    "@eslint/css": "^0.10.0",
    "@eslint/js": "^9.32.0",
    "eslint": "^9.32.0",
    "globals": "^16.3.0"
  }
}
```

**Section sources**
- [requirements.txt](file://requirements.txt#L0-L22)
- [package.json](file://package.json#L0-L10)

## Backward Compatibility and Core Modifications

When modifying core components like `controller.py`, backward compatibility must be maintained. The `controller.py` file manages the lifecycle of trading bots and serves as a critical integration point between the web interface and trading execution.

Key considerations for core modifications:
- Preserve existing function signatures and return value formats
- Maintain database schema compatibility
- Ensure API endpoints continue to accept existing request formats
- Provide migration paths for configuration changes

The `controller.py` file demonstrates careful handling of data transformations:
```python
# Handle field name translation between frontend and database
if 'check_interval_seconds' in data:
    data['interval'] = data.pop('check_interval_seconds')
```

This pattern allows the system to evolve while maintaining compatibility with existing client code. Any changes to core components should include comprehensive testing to ensure existing functionality is not disrupted.

**Section sources**
- [core/bots/controller.py](file://core/bots/controller.py#L0-L176)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L0-L169)

## Unit Testing Guidelines

Unit tests should be written to cover the following aspects:

**Test Coverage Requirements**
- All public functions and methods
- Edge cases and error conditions
- Critical business logic in trading strategies
- Data validation and transformation routines

**Test Structure**
- Use descriptive test function names
- Follow arrange-act-assert pattern
- Isolate dependencies using mocks where appropriate
- Include clear assertions with meaningful error messages

**Strategy Testing**
- Test each trading strategy with historical data
- Verify signal generation under various market conditions
- Validate risk management calculations
- Ensure proper trade execution logic

Example test structure for a trading strategy:
```python
def test_bollinger_squeeze_strategy():
    # Arrange: Create test data
    df = create_test_candlestick_data()
    
    # Act: Execute strategy analysis
    result = strategy.analyze(df)
    
    # Assert: Verify expected signals
    assert result["signal"] in ["BUY", "SELL", "HOLD"]
    assert "explanation" in result
```

Tests should be added for any new features and existing tests must pass when submitting changes.

**Section sources**
- [core/strategies/strategy_map.py](file://core/strategies/strategy_map.py#L0-L27)
- [core/bots/trading_bot.py](file://core/bots/trading_bot.py#L0-L169)