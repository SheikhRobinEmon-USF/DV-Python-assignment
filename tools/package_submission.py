"""Build the complete submission only after all required deliverables are verified."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import nbformat

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def preflight(python_only=False):
    problems=[]
    notebooks=sorted((ROOT/'notebooks').glob('*.ipynb'))
    if len(notebooks)!=5:
        problems.append('Exactly five notebooks are required.')
    for path in notebooks:
        nb=nbformat.read(path,as_version=4)
        try:
            nbformat.validate(nb)
        except Exception as error:
            problems.append(f'{path.name}: notebook structure invalid: {error}')
        code=[c for c in nb.cells if c.cell_type=='code']
        if not code or any(c.execution_count is None for c in code):
            problems.append(f'{path.name}: unexecuted cells.')
        if any(o.output_type=='error' for c in code for o in c.get('outputs',[])):
            problems.append(f'{path.name}: execution errors.')
        if not any(o.output_type in {'display_data','execute_result'} and 'image/png' in o.get('data',{}) for c in code for o in c.get('outputs',[])):
            problems.append(f'{path.name}: no rendered figure output.')
        evidence=nb.metadata.get('assignment',{})
        if evidence.get('course_data_execution')!='passed':
            problems.append(f'{path.name}: no successful course-data execution record.')
        for name,digest in evidence.get('input_sha256',{}).items():
            path_input=ROOT/name
            if not path_input.is_file() or sha(path_input)!=digest:
                problems.append(f'{path.name}: input changed since execution: {name}')
    for stem in ['01_unemployment_obesity','02_pasco_covid','03_hillsborough_covid','04_european_car_sales','05_broward_palm_beach']:
        for extension in ['png','pdf','svg']:
            if not (ROOT/'figures'/f'{stem}.{extension}').is_file():
                problems.append(f'Missing figure {stem}.{extension}')
    if not (ROOT/'data/2 yearly.zip').is_file():
        problems.append('Missing original yearly ZIP; do not substitute reduced data.')
    if not (ROOT/'data/derived/reconstructed_covid.csv').is_file():
        problems.append('Missing reconstructed county/day source.')
    if not python_only:
        settings=json.loads((ROOT/'config/assignment.json').read_text())['tableau']
        path=ROOT/settings['path']
        if not path.is_file():
            problems.append('Missing final Module 3 Tableau packaged workbook: '+settings['path'])
        else:
            try:
                with zipfile.ZipFile(path) as archive:
                    bad=archive.testzip()
                    if bad: problems.append(f'Tableau archive corrupt at {bad}')
                    twbs=[x for x in archive.namelist() if x.lower().endswith('.twb')]
                    if len(twbs)!=1:
                        problems.append('The Tableau package must contain one workbook definition.')
                    else:
                        xml=archive.read(twbs[0]); ET.fromstring(xml)
                        text=xml.decode('utf-8').casefold()
                        if 'script_str' not in text or 'lucrative' not in text:
                            problems.append('No identifiable Python profitability calculation in workbook.')
            except (zipfile.BadZipFile,ET.ParseError,UnicodeError) as error:
                problems.append(f'Invalid Tableau package: {error}')
        if not settings.get('desktop_verified') or not settings.get('verification_notes','').strip():
            problems.append('Tableau Desktop connection and reopened workbook have not been verified; record the actual result.')
    return problems


def selected_files():
    root_files=['README.md','SUBMISSION_GUIDE.md','requirements.txt']
    files=[ROOT/name for name in root_files]
    for directory in ['notebooks','scripts','dv_assignment','tools','config','reports','tableau','figures','tests']:
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith(('.pyc','.log')))
    files.extend((ROOT/'data').glob('*.xlsx'))
    files.append(ROOT/'data/2 yearly.zip')
    files.extend([ROOT/'data/derived/reconstructed_covid.csv',ROOT/'data/derived/reconstruction_audit.json'])
    return sorted(set(p for p in files if p.is_file()))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--python-only',action='store_true',help='Create a clearly labeled partial package, excluding a final-submission claim.')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    problems=preflight(args.python_only)
    if problems:
        print('Not ready for '+('Python packaging:' if args.python_only else 'final submission:'))
        for problem in problems: print('- '+problem)
        return 1
    if args.check:
        print('All '+('Python' if args.python_only else 'final-submission')+' deliverables passed preflight.')
        return 0
    destination=ROOT/'dist'; destination.mkdir(exist_ok=True)
    name='python_deliverables.zip' if args.python_only else 'assignment_submission.zip'
    target=destination/name
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in selected_files():
            # A ZIP around the original ZIP is lossless; store it directly.
            method=zipfile.ZIP_STORED if path.suffix.lower()=='.zip' else zipfile.ZIP_DEFLATED
            archive.write(path,Path('DV-Python-assignment')/path.relative_to(ROOT),compress_type=method)
        archive.writestr('DV-Python-assignment/PACKAGE_STATUS.txt',
            'Python deliverables only; final Module 3 Tableau workbook and Desktop validation are still required.\n' if args.python_only else 'Complete deliverable package; see reports and Tableau verification notes.\n')
    with zipfile.ZipFile(target) as archive:
        bad=archive.testzip()
        if bad: raise ValueError(f'ZIP integrity failure: {bad}')
    print(f'Created {target} ({target.stat().st_size:,} bytes).')
    return 0


if __name__=='__main__':
    sys.exit(main())
