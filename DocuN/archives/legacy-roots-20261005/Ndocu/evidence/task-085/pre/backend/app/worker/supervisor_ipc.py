"""Bounded one-shot SUP exchange through a named page-file mapping.

The request is written before Resume. The parent reads the response only after
the exact SUP process exits. No pipe read/write or background sender can block
past the management deadline. A torn frame is never interpreted as a result.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import json
import os
import re
import struct


MAP_SIZE = 16_384
SLOT_SIZE = MAP_SIZE // 2
REQUEST_OFFSET = 0
RESULT_OFFSET = SLOT_SIZE
_FRAME_HEADER = 36  # uint32 length + SHA-256
ERROR_ALREADY_EXISTS = 183
PAGE_READWRITE = 0x04
FILE_MAP_READ = 0x0004
FILE_MAP_WRITE = 0x0002
_MAPPING_NAME = re.compile(r"Local\\RetroLume\.SUP\.[0-9a-f]{32}\Z")


class IpcUnknown(RuntimeError):
    pass


def validate_name(name: str) -> str:
    if type(name) is not str or _MAPPING_NAME.fullmatch(name) is None:
        raise ValueError("invalid SUP mapping name")
    return name


def pack_frame(value: dict, *, capacity: int = SLOT_SIZE) -> bytes:
    if type(value) is not dict:
        raise TypeError("SUP frame must be an object")
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if not payload or len(payload) > capacity - _FRAME_HEADER:
        raise IpcUnknown("SUP frame exceeds bounded slot")
    return struct.pack("<I", len(payload)) + hashlib.sha256(payload).digest() + payload


def unpack_frame(raw: bytes, *, capacity: int = SLOT_SIZE) -> dict:
    if type(raw) is not bytes or len(raw) != capacity:
        raise IpcUnknown("SUP frame slot length invalid")
    length = struct.unpack_from("<I", raw)[0]
    if length == 0 or length > capacity - _FRAME_HEADER:
        raise IpcUnknown("SUP frame incomplete or oversized")
    expected = raw[4:36]
    payload = raw[36:36 + length]
    if hashlib.sha256(payload).digest() != expected:
        raise IpcUnknown("SUP frame checksum mismatch")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise IpcUnknown("SUP frame JSON invalid") from exc
    if type(value) is not dict:
        raise IpcUnknown("SUP frame root must be object")
    return value


def _kernel():
    if os.name != "nt":
        raise IpcUnknown("Windows mapping unavailable")
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateFileMappingW.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
                                        wintypes.DWORD, wintypes.DWORD, wintypes.LPCWSTR]
    api.CreateFileMappingW.restype = wintypes.HANDLE
    api.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    api.OpenFileMappingW.restype = wintypes.HANDLE
    api.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.DWORD, ctypes.c_size_t]
    api.MapViewOfFile.restype = ctypes.c_void_p
    api.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
    api.UnmapViewOfFile.restype = wintypes.BOOL
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    return api


class NamedMapping:
    def __init__(self, api, handle, view: int, name: str):
        self.api = api
        self.handle = handle
        self.view = view
        self.name = name

    @classmethod
    def create(cls, name: str) -> "NamedMapping":
        validate_name(name)
        api = _kernel()
        ctypes.set_last_error(0)
        handle = api.CreateFileMappingW(ctypes.c_void_p(-1), None, PAGE_READWRITE, 0, MAP_SIZE, name)
        error = ctypes.get_last_error()
        if not handle or error == ERROR_ALREADY_EXISTS:
            if handle:
                api.CloseHandle(handle)
            raise IpcUnknown(f"SUP mapping create/collision: Windows error {error}")
        view = api.MapViewOfFile(handle, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, MAP_SIZE)
        if not view:
            api.CloseHandle(handle)
            raise IpcUnknown(f"SUP mapping view: Windows error {ctypes.get_last_error()}")
        return cls(api, handle, view, name)

    @classmethod
    def open_existing(cls, name: str) -> "NamedMapping":
        validate_name(name)
        api = _kernel()
        handle = api.OpenFileMappingW(FILE_MAP_READ | FILE_MAP_WRITE, False, name)
        if not handle:
            raise IpcUnknown(f"SUP mapping open: Windows error {ctypes.get_last_error()}")
        view = api.MapViewOfFile(handle, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, MAP_SIZE)
        if not view:
            api.CloseHandle(handle)
            raise IpcUnknown(f"SUP mapping view: Windows error {ctypes.get_last_error()}")
        return cls(api, handle, view, name)

    def _write(self, offset: int, value: dict) -> None:
        frame = pack_frame(value)
        # A nonzero length is the final commit marker; process exit is the read barrier.
        ctypes.memset(self.view + offset, 0, 4)
        ctypes.memmove(self.view + offset + 4, frame[4:], len(frame) - 4)
        ctypes.memmove(self.view + offset, frame[:4], 4)

    def _read(self, offset: int) -> dict:
        return unpack_frame(ctypes.string_at(self.view + offset, SLOT_SIZE))

    def write_request(self, value: dict) -> None:
        self._write(REQUEST_OFFSET, value)

    def read_request(self) -> dict:
        return self._read(REQUEST_OFFSET)

    def write_result(self, value: dict) -> None:
        self._write(RESULT_OFFSET, value)

    def read_result(self) -> dict:
        return self._read(RESULT_OFFSET)

    def close(self) -> None:
        failures = []
        if self.view:
            if self.api.UnmapViewOfFile(self.view):
                self.view = 0
            else:
                failures.append("UnmapViewOfFile")
        if self.handle:
            if self.api.CloseHandle(self.handle):
                self.handle = None
            else:
                failures.append("CloseHandle(mapping)")
        if failures:
            raise IpcUnknown("/".join(failures))

