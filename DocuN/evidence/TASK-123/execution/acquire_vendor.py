"""只获取锁定的官方纯数据，拒绝执行远程代码、权重和未知重定向。"""
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request

OUT = Path(__file__).resolve().parent / "vendor-data"
LIMIT = 64 * 1024 * 1024
TOTAL = 128 * 1024 * 1024
HOSTS = {"huggingface.co", "cdn.deepseek.com", "cas-bridge.xethub.hf.co"}

class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.chain = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname not in HOSTS:
            raise ValueError("unapproved_redirect")
        self.chain.append({"status": code, "from": req.full_url, "to": newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def get(url, name):
    OUT.mkdir(exist_ok=True)
    target = OUT / name
    assert target.resolve().parent == OUT.resolve()
    assert not target.exists(), "不得覆盖原件"
    redirects = Redirects()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), redirects)
    started = time.monotonic()
    row = {"url": url, "saved_as": name, "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "RetroLume-TASK123-offline-evidence", "Accept-Encoding": "identity"})
        with opener.open(request, timeout=60) as response:
            if int(response.headers.get("Content-Length", "0")) > LIMIT:
                raise ValueError("single_file_limit")
            data = bytearray()
            while True:
                if time.monotonic() - started > 60:
                    raise TimeoutError("request_time_limit")
                chunk = response.read(min(1024 * 1024, LIMIT + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
                if len(data) > LIMIT:
                    raise ValueError("single_file_limit")
            prior = sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
            if prior + len(data) > TOTAL:
                raise ValueError("total_limit")
            target.write_bytes(data)
            row.update(status="saved", final_url=response.url, redirects=redirects.chain,
                       bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                       content_type=response.headers.get("Content-Type"),
                       response_commit=response.headers.get("X-Repo-Commit"))
    except Exception as exc:
        row.update(status="failed", error_type=type(exc).__name__, redirects=redirects.chain)
    row["elapsed_seconds"] = time.monotonic() - started
    with (OUT.parent / "download-ledger.jsonl").open("a", encoding="utf-8") as ledger:
        ledger.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False))
    return target if row["status"] == "saved" else None

if __name__ == "__main__":
    repo = "deepseek-ai/DeepSeek-V4.1-Flash-1017"
    if sys.argv[1] == "metadata":
        get("https://huggingface.co/api/models/" + repo, "ds1017-model-metadata.json")
    elif sys.argv[1] == "files":
        metadata = json.loads((OUT / "ds1017-model-metadata.json").read_bytes())
        assert metadata["id"] == repo and metadata["author"] == "deepseek-ai"
        commit = metadata["sha"]
        assert re.fullmatch(r"[0-9a-f]{40}", commit)
        available = {x["rfilename"] for x in metadata["siblings"]}
        for name in sys.argv[2:]:
            assert name in {"README.md", "LICENSE", "config.json", "tokenizer_config.json", "tokenizer.json", "chat_template.jinja"}
            if name not in available:
                print(json.dumps({"absent_from_metadata": name}))
                continue
            get("https://huggingface.co/" + repo + "/resolve/" + commit + "/" + name, "ds1017-" + name)
