# Type Checker Analysis: ty vs pyright

This directory contains comprehensive test cases to investigate the specific gaps between ty and pyright regarding protocols and generics support.

## Test Structure

### Protocol Support Analysis
- `protocol_tests/` - Tests for different protocol scenarios
  - `structural_subtyping.py` - Tests for structural typing behavior
  - `missing_methods.py` - Tests for missing method detection
  - `wrong_signatures.py` - Tests for incorrect method signature detection
  - `protocol_inheritance.py` - Tests for protocol inheritance scenarios
  - `runtime_checkable.py` - Tests for runtime_checkable protocol behavior

### Generics Support Analysis
- `generics_tests/` - Tests for generic type checking capabilities
  - `basic_generics.py` - Basic generic classes and functions
  - `generic_constraints.py` - Generic type constraints and bounds
  - `variance_tests.py` - Covariance and contravariance tests
  - `advanced_generics.py` - Advanced generic features
  - `generic_protocols.py` - Generic protocol combinations

### Configuration Investigation
- `config_tests/` - Tests for different configuration scenarios
  - `pyright_strict.py` - Tests with strict pyright configuration
  - `pyright_lenient.py` - Tests with lenient pyright configuration
  - `ty_default.py` - Tests with default ty configuration

## Running Tests

1. Install ty: `pip install ty`
2. Run pyright tests: `uv run pyright type_checker_analysis/`
3. Run ty tests: `ty type_checker_analysis/`

## Analysis Results

Results will be documented in `analysis_results.md` after running all tests.
