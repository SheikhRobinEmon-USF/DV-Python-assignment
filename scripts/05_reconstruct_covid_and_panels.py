"""Requirements 5–6: reconstruct from both case files, then draw a 2 by 2 figure."""
import _bootstrap
from dv_assignment.workflows import reconstruction

if __name__=='__main__':
    source,broward,palm,figure=reconstruction()
    print(f'Reconstructed {len(source):,} county/date rows from both yearly inputs.')
    print(source.attrs['source_audit'])
