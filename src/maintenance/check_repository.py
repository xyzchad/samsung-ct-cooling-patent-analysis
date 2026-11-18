"""Check navigation, preserved inputs and the relocation manifest (stdlib only)."""
import csv,hashlib,json,re
from pathlib import Path
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[2]
errors=[]; links=0
for p in ROOT.rglob('*.md'):
 if any(x in p.relative_to(ROOT).parts for x in ['node_modules','.git','.plotcache','local_review']):continue
 text=p.read_text()
 for m in re.finditer(r'\]\(([^\n]*?)\)',text):
  raw=m.group(1).strip('<>'); parsed=urlsplit(raw)
  if not raw or raw.startswith(('#','mailto:')):continue
  if parsed.scheme:
   if parsed.netloc in ['github.com','raw.githubusercontent.com']:
    path=unquote(parsed.path)
    mm=re.match(r'/(?:youngjei|xyzchad)/samsung-ct-cooling-patent-analysis/(?:blob/main/|tree/main/|main/)(.*)',path)
    if not mm:continue
    target=ROOT/mm.group(1)
   else:continue
  else:target=p.parent/unquote(parsed.path)
  links+=1
  if not target.exists():errors.append(f'{p.relative_to(ROOT)}: {raw}')

preserved=0; moved=0
with (ROOT/'docs/file_moves.csv').open(encoding='utf-8-sig') as f:
 for row in csv.DictReader(f):
  p=ROOT/row['current_path'];moved+=1
  if not p.exists():errors.append('Missing moved file: '+row['current_path']);continue
  # Original inputs and reference workbooks must retain their bytes.
  if p.suffix=='.xlsx' or row['current_path'].startswith(('data/raw/','data/processed/us_baseline/','archive/2026-11-08_wrong_date_filter/')):
   actual=hashlib.sha256(p.read_bytes()).hexdigest()
   if actual!=row['original_sha256']:errors.append('Changed preserved input: '+row['current_path'])
   preserved+=1

report={'passed':not errors,'markdown_links_checked':links,'moved_files_present':moved,
 'preserved_input_hashes_checked':preserved,'errors':errors}
dest=ROOT/'docs/validation/repository.json';dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
