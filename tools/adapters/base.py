# base adapter interface, like:
# class ToolAdapter:
#     async def available(self) -> bool
#     async def run(self, **kwargs) -> ToolResult
# Where ToolResult is a class that holds:
# 
# stdout (text / JSON),
# 
# stderr,
# 
# exit_code,
# 
# possibly parsed data (if JSON or other parseable format),
# 
# maybe a flag for timeout or failure.
# 
# The other adapters should implement this interface.