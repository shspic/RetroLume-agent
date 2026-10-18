"""Reject UNC executable/cwd so validation cannot trigger an outbound share lookup."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "backend/app/worker/command.py"
data = path.read_text(encoding="utf-8")
old = '        if type(self.executable) is not str or not os.path.isabs(self.executable) or not os.path.isfile(self.executable):\n'
new = '        if type(self.executable) is not str or self.executable.startswith("\\\\") or not os.path.isabs(self.executable) or not os.path.isfile(self.executable):\n'
assert data.count(old) == 1
data = data.replace(old, new)
old = '        if type(self.cwd) is not str or not os.path.isabs(self.cwd) or not os.path.isdir(self.cwd):\n'
new = '        if type(self.cwd) is not str or self.cwd.startswith("\\\\") or not os.path.isabs(self.cwd) or not os.path.isdir(self.cwd):\n'
assert data.count(old) == 1
path.write_text(data.replace(old, new), encoding="utf-8", newline="")
