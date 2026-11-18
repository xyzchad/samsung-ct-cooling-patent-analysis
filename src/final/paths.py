"""Canonical repository locations shared by the final analysis scripts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'data/processed/us_baseline'
REVIEWED = ROOT / 'data/processed/us_reviewed'
REFERENCE = ROOT / 'data/reference'
CLAIMS = ROOT / 'data/raw/patent_claims'
RESULTS = ROOT / 'data/results/final'
DELIVERABLES = ROOT / 'deliverables'
FIGURES = DELIVERABLES / 'figures'
DOCS = ROOT / 'docs'
VALIDATION = DOCS / 'validation'

for directory in [REVIEWED, RESULTS, DELIVERABLES, FIGURES / 'editable', VALIDATION]:
    directory.mkdir(parents=True, exist_ok=True)
