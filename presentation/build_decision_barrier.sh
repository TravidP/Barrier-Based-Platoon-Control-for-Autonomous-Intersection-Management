#!/bin/sh
# Build in a temporary directory; only final PDFs are copied beside the sources.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
build_dir=$(mktemp -d "${TMPDIR:-/tmp}/decision-barrier.XXXXXX")
trap 'rm -rf "$build_dir"' EXIT HUP INT TERM
for lang in en zh; do
  mkdir -p "$build_dir/$lang"
  latexmk -xelatex -interaction=nonstopmode -halt-on-error \
    -outdir="$build_dir/$lang" "decision_barrier_$lang.tex"
  cp "$build_dir/$lang/decision_barrier_$lang.pdf" "decision_barrier_$lang.pdf"
done
printf '%s\n' 'Built decision_barrier_en.pdf and decision_barrier_zh.pdf (18 pages each).'
