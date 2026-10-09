#!/usr/bin/env bash
set -euo pipefail

tag="${LANGUAGE_TAG:?set language-tag to a GitHub Release tag such as v0.7.0-alpha.2}"
repo="${LANGUAGE_REPOSITORY:?set language-repository}"
wheel="${LANGUAGE_WHEEL:?set language-wheel to the exact release filename}"
dest="${RUNNER_TEMP:-/tmp}/mint-action-install"
mkdir -p "$dest"

base="https://github.com/${repo}/releases/download/${tag}"
curl -fsSL "${base}/SHA256SUMS" -o "${dest}/SHA256SUMS"
curl -fsSL "${base}/${wheel}" -o "${dest}/${wheel}"

if ! grep -F "$wheel" "${dest}/SHA256SUMS" >/dev/null; then
  echo "SHA256SUMS does not list ${wheel}; set language-wheel to a file on ${tag}" >&2
  exit 1
fi

(
  cd "$dest"
  grep -F "$wheel" SHA256SUMS | shasum -a 256 -c -
)

python -m venv "${dest}/venv"
"${dest}/venv/bin/pip" install --no-cache-dir --no-index "${dest}/${wheel}"
echo "${dest}/venv/bin" >> "${GITHUB_PATH}"
"${dest}/venv/bin/mint" version
