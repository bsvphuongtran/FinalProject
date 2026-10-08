#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m pytest "$@"
if command -v allure >/dev/null 2>&1; then
  allure generate allure-results -o allure-report --clean
  allure open allure-report
else
  echo "Allure CLI is not installed. Results are in allure-results/."
fi
