"""Restore full-size CSVs from the original uploaded lossless ZIP, with SHA-256 checks."""
import hashlib
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    '2020 Cases only.csv':('7249233799148213cea40b2a2df3c7b8eda90419f8ebb2fe32a078cb18dc5c5e',180989600),
    '2021 Cases only.csv':('b311a9e0290dfde3fbeb23afb4665a09fbd2e0de885063e6c4ecfc3448daedb6',124852254),
}


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def prepare():
    archive=ROOT/'data/2 yearly.zip'
    if not archive.is_file():
        raise FileNotFoundError('Restore the original data/2 yearly.zip before continuing.')
    with zipfile.ZipFile(archive) as source:
        for name,(digest,size) in EXPECTED.items():
            dest=ROOT/'data'/name
            if not dest.exists():
                members=[x for x in source.infolist() if Path(x.filename).name==name and not x.filename.startswith('__MACOSX/')]
                if len(members)!=1 or members[0].file_size!=size:
                    raise ValueError(f'Unexpected archive member or original size: {name}')
                # Extract only the named course data, avoiding paths and macOS metadata.
                temporary=dest.with_suffix('.csv.extracting')
                try:
                    with source.open(members[0]) as input_stream,temporary.open('xb') as output_stream:
                        shutil.copyfileobj(input_stream,output_stream)
                    if sha(temporary)!=digest:
                        raise ValueError(f'Checksum mismatch: {name}')
                    temporary.replace(dest)
                finally:
                    temporary.unlink(missing_ok=True)
            if dest.stat().st_size!=size or sha(dest)!=digest:
                raise ValueError(f'Existing {name} differs from the full original; preserving it for inspection.')
            print(f'Verified original: {name} ({size:,} bytes)')


if __name__=='__main__':
    prepare()
