#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-multilingual-content-translator}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Log in to GitHub (use: divyansh.2392@gmail.com)"
  gh auth login --hostname github.com --git-protocol https --web
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "Pushing to existing remote..."
  git push -u origin main
else
  echo "Creating private repo: $REPO_NAME"
  gh repo create "$REPO_NAME" \
    --private \
    --source=. \
    --remote=origin \
    --push \
    --description "Multi-agent multilingual travel content translator"
fi

echo "Done. Repo URL:"
gh repo view --json url -q .url
