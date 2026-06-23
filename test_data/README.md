# Test Data

This directory contains all sample and test data. The application code does not depend on this directory at runtime.

## Layout

```text
original_examples/
  国语转拼音/
  粤语转拼音/
  英语音译改写/
  闽南语转台罗拼音/
  谐音字替换/
corpus/
  mandarin/
  cantonese/
  english/
outputs/
  mandarin/
  cantonese/
  english/
```

- `original_examples/`: the four original examples provided for the project.
- `original_examples/谐音字替换/`: a small sample for the homophone replacement mode.
- `corpus/`: extra public-domain, traditional, or openly licensed lyrics used for broader testing.
- `outputs/`: generated conversion outputs from previous test runs.

When migrating the converter application, copy `lyrics_converter/`, `convert.py`, `app.py`, `requirements.txt`, `README.md`, and `ARCHITECTURE.md`. Copy `test_data/` only when examples or regression data are needed.
