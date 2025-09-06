# Notice
This is a board support package (BSP) directory for NuttX. It cannot be built independently - requires full NuttX and apps repositories.

# Code Style
- Follow LLVM formatting (.clang-format): 2-space indent, 80-column limit
- C code with Apache 2.0 license headers on all files
- NuttX conventions: snake_case for functions, UPPER_CASE for macros
- Error handling: return negative error codes, use syslog for debugging
- Include order: nuttx/config.h first, then system headers, then local headers
