"""Execute selected notebooks; preserve failures and write current-run evidence."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import hashlib
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--through',type=int,choices=range(1,6),default=5)
parser.add_argument('--kernel',default='python3')
args=parser.parse_args()

def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
for path in sorted((ROOT/'notebooks').glob('*.ipynb'))[:args.through]:
    print('Executing',path.name,flush=True)
    nb=nbformat.read(path,as_version=4)
    try:
        NotebookClient(nb,timeout=180,kernel_name=args.kernel,
                       resources={'metadata':{'path':str(ROOT/'notebooks')}}).execute()
    except Exception as error:
        # Keep the existing successful notebook; persist a separate failure log.
        (ROOT/'reports'/f'{path.stem}_execution_failure.txt').write_text(str(error))
        print(f'FAILED: {path.name}: {error}',file=sys.stderr)
        raise SystemExit(1)
    nb.metadata.setdefault('assignment',{})['course_data_execution']='passed'
    nb.metadata['assignment']['executed_utc']=datetime.now(timezone.utc).isoformat()
    nb.metadata['assignment']['input_sha256']={str(p.relative_to(ROOT)):file_hash(p)
            for p in sorted((ROOT/'data').glob('*')) if p.is_file() and p.suffix.lower() in {'.xlsx','.zip'}}
    nbformat.write(nb,path)
    print('Passed',path.name,flush=True)
