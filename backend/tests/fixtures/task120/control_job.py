"""Use the unchanged native Job implementation without app.worker exports.

Only finite TESTONLY controllers import this module. Production SUP/worker
imports, Job ABI, names, security, limits and code bytes are unchanged.
"""
import hashlib
import importlib.util
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[3]/'app/worker/windows_job.py'
SOURCE_SHA256=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
_spec=importlib.util.spec_from_file_location('task120_native_job_control',SOURCE)
_native=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_native)
NamedJob=_native.NamedJob
JobOpenError=_native.JobOpenError
_EXTENDED_LIMIT=_native._EXTENDED_LIMIT
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS=_native.JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS
JOB_OBJECT_LIMIT_ACTIVE_PROCESS=_native.JOB_OBJECT_LIMIT_ACTIVE_PROCESS
JOB_OBJECT_LIMIT_JOB_MEMORY=_native.JOB_OBJECT_LIMIT_JOB_MEMORY
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE=_native.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
