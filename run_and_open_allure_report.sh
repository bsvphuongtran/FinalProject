#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# python -m pytest "$@"
# NNTT: do ở macbook và windows lệnh run khác nhau nên em nghĩ file .sh neeu viết cho car 2 trường hợp này
if python3 -c "import sys" >/dev/null 2>&1; then
  PYTHON=python3
elif python -c "import sys" >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python was not found. Install Python 3 and make sure python3 or python is on PATH." >&2
  exit 1
fi

# Keep going when tests fail so the report is still generated and opened.
pytest_status=0
"$PYTHON" -m pytest "$@" || pytest_status=$?

if command -v allure >/dev/null 2>&1; then
  allure generate allure-results -o allure-report --clean
  allure open allure-report
else
  echo "Allure CLI is not installed. Results are in allure-results/."
fi

exit "$pytest_status"
