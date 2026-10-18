from control import HERE,event
path=HERE/'http_flows.py';raw=path.read_text(encoding='utf-8')
start=raw.index("        aid=ids['teaching']\n");end=raw.index("        aid=ids['interview']\n",start)
part=raw[start:end]
if "if not self.proof.get('teaching_final')" in raw:raise RuntimeError('already_patched')
raw=raw[:start]+"        if not self.proof.get('teaching_final'):\n"+''.join('    '+line if line.strip() else line for line in part.splitlines(keepends=True))+raw[end:]
path.write_text(raw,encoding='utf-8',newline='\n');event('http_driver_resume_preserves_completed_teaching')
