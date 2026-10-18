"""内容寻址原件库。仅用于应用独占、可信本地目录。

文件发布与数据库提交不是一个事务：调用方必须先成功发布原件，再在
PostgreSQL提交来源版本。数据库失败留下未引用原件，不得破坏旧活动版。
不自动清理未引用文件；跨存储协调和外部进程同时篡改属于后续集成边界。
"""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import BinaryIO


class IntegrityError(ValueError):
    """已存在的原件不再匹配其内容指纹。"""


@dataclass(frozen=True)
class Original:
    sha256: str
    size: int


class OriginalStore:
    def __init__(self, root: Path):
        root = Path(root)
        if not root.is_absolute():
            raise ValueError("原件目录必须为绝对路径")
        self.root = root
        self._check_root()

    @staticmethod
    def _reject_redirect(path: Path) -> os.stat_result:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("不允许符号链接或重解析点")
        return info

    def _check_root(self) -> None:
        # 不解析后才检查，以免隐藏调用方路径中的重定向。
        for path in reversed((self.root, *self.root.parents)):
            if not stat.S_ISDIR(self._reject_redirect(path).st_mode):
                raise ValueError("原件目录必须存在且为目录")

    def _path(self, key: str) -> Path:
        if not isinstance(key, str) or re.fullmatch(r"[0-9a-f]{64}", key) is None:
            raise ValueError("无效原件指纹")
        self._check_root()
        return self.root / key

    @staticmethod
    def _limit(max_bytes: int) -> None:
        if type(max_bytes) is not int or max_bytes <= 0:
            raise ValueError("必须给出正整数大小上限")

    def put(self, source: BinaryIO, *, max_bytes: int) -> Original:
        """流式保存；未完成写入不发布，不覆盖已存在的原件。"""
        self._limit(max_bytes)
        self._check_root()
        digest = hashlib.sha256()
        size = 0
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(prefix=".incoming-", dir=self.root, delete=False) as output:
                temporary = Path(output.name)
                while True:
                    chunk = source.read(min(65536, max_bytes - size + 1))
                    if not isinstance(chunk, bytes):
                        raise TypeError("原件输入必须为二进制流")
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > max_bytes:
                        raise ValueError("原件超过大小上限")
                    digest.update(chunk)
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
            original = Original(digest.hexdigest(), size)
            destination = self._path(original.sha256)
            try:
                # 同卷硬链接提供原子、不得覆盖的发布；不支持则明确失败。
                os.link(temporary, destination)
            except FileExistsError:
                # 幂等命中也验证已存内容，不能用被篡改文件冒充成功。
                self.verify(original)
            return original
        finally:
            if temporary is not None:
                # 只删除本调用创建的一个临时文件，从不删除发布的原件。
                temporary.unlink(missing_ok=True)

    def verify(self, original: Original) -> None:
        if type(original.size) is not int or original.size < 0:
            raise ValueError("无效原件长度")
        path = self._path(original.sha256)
        info = self._reject_redirect(path)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("原件必须为普通文件")
        if info.st_size != original.size:
            raise IntegrityError("原件长度不匹配")
        digest = hashlib.sha256()
        count = 0
        with path.open("rb") as stream:
            while chunk := stream.read(min(65536, original.size - count + 1)):
                count += len(chunk)
                if count > original.size:
                    raise IntegrityError("原件在读取时变化")
                digest.update(chunk)
        if count != original.size or digest.hexdigest() != original.sha256:
            raise IntegrityError("原件内容指纹不匹配")

    def read(self, original: Original, *, max_bytes: int) -> bytes:
        """有界回查并核对返回字节；不返回任意本地路径。"""
        self._limit(max_bytes)
        if type(original.size) is not int or original.size < 0:
            raise ValueError("无效原件长度")
        if original.size > max_bytes:
            raise ValueError("原件超过读取上限")
        path = self._path(original.sha256)
        if not stat.S_ISREG(self._reject_redirect(path).st_mode):
            raise ValueError("原件必须为普通文件")
        with path.open("rb") as stream:
            content = stream.read(original.size + 1)
        if len(content) != original.size or hashlib.sha256(content).hexdigest() != original.sha256:
            raise IntegrityError("原件内容指纹不匹配")
        return content
