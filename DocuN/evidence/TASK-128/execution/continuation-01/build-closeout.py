from pathlib import Path
E=Path(__file__).absolute().parent
s=(E.parent/'finalize.py').read_text(encoding='utf-8')
s=s.replace('R=E.parents[3]','R=E.parents[4]')
s=s.replace("[E,E/'entry-04',E/'entry-05',E/'entry-05-ready']","[E,E/'entry-06']")
(E/'closeout.py').write_text(s,encoding='utf-8')
