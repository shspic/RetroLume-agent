"""真正运行前检查Windows自管socketpair和固定协议适配，零业务资源。"""
import asyncio
import socket
import unittest
from unittest.mock import patch
from app.runtime import psycopg_compatible_loop_factory
from tests.fixtures.task097.network import install


class FixturePreflightTests(unittest.TestCase):
    def test_guard_keeps_python_selfpipe_but_blocks_non_task_destinations(self):
        with patch.object(socket.socket,"connect",socket.socket.connect),patch.object(socket.socket,"connect_ex",socket.socket.connect_ex),\
                patch.object(socket,"getaddrinfo",socket.getaddrinfo),patch.object(socket,"socketpair",socket.socketpair):
            install()
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
                async def value():return 97
                self.assertEqual(runner.run(value()),97)
            for address in [("api.deepseek.com",443),("127.0.0.1",8000),("192.0.2.1",443)]:
                with socket.socket() as probe:
                    with self.assertRaises(OSError):probe.connect(address)
            with self.assertRaises(OSError):socket.getaddrinfo("api.deepseek.com",443)
