## Project Overview
This project is a Python MCP server (`ipynb-mcp`) that loads and edits Jupyter notebooks via tool APIs, built with `mcp[cli]` and `notebookllm`.

## Structure Map
- `mcp_server.py` - Main server implementation; defines all MCP tools (`load_notebook`, conversion, add/edit/remove/save cell flows) and in-memory notebook state.
- `docs/` - Design notes and reference docs used for implementation context (not runtime code).
- `README.md` - User-facing setup, tool behavior, and client integration examples.
- `pyproject.toml` - Package metadata, dependencies, and CLI entrypoint (`ipynb-mcp`).
- `uv.lock` - Locked dependency graph for reproducible `uv` environments.

## Development Guide
- Build: `uv build`
- Run server locally: `uv run ipynb-mcp`
- Tests: no formal automated test suite is currently defined; do a smoke check with MCP Inspector: `npx @modelcontextprotocol/inspector uvx ipynb-mcp --from git+https://github.com/g0g5/jupyternotebook-mcp@main`
- Typechecks: no dedicated typecheck config is present; run a quick syntax gate before shipping: `uv run python -m py_compile mcp_server.py`
- Verify changes: confirm build succeeds and manually exercise key tools (`load_notebook`, `add_cell`, `edit_cell`, `remove_cell`, `save_loaded_notebook`) in Inspector.
