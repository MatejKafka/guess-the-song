import asyncio
import builtins


def _blocked_input(*_, **__):
	raise RuntimeError("input() not allowed, use ainput() instead")

_real_input = builtins.input
builtins.input = _blocked_input


async def ainput(*args, **kwargs) -> str:
	loop = asyncio.get_running_loop()
	return await loop.run_in_executor(None, lambda: _real_input(*args, **kwargs))
