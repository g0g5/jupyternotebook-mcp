# Jupyter Notebook MCP

A Model Context Protocol server for working with Jupyter Notebooks (`.ipynb` files) in a way that is efficient for Large Language Models (LLMs). It converts notebooks to a simplified plain text format to reduce token usage and cost, and can convert them back.

## Available Tools

*   **`load_notebook`**: Loads a `.ipynb` file into memory.
    *   **Arguments**:
        *   `filepath` (string): The absolute path to the `.ipynb` file.
    *   **Returns**: (string) Success or failure message, including cell count.
*   **`notebook_to_plain_text`**: Converts a `.ipynb` file (loaded or from path) to a simplified plain text representation.
    *   **Arguments**:
        *   `input_filepath` (string, optional): Absolute path to the `.ipynb` file for on-the-fly conversion.
    *   **Returns**: (string) Plain text representation or error message.
*   **`plain_text_to_notebook_file`**: Converts plain text content back to a `.ipynb` file and saves it.
    *   **Arguments**:
        *   `plain_text_content` (string): Plain text content to convert.
        *   `output_filepath` (string): Absolute path to save the `.ipynb` file (must end with `.ipynb`).
    *   **Returns**: (string) Success or failure message.
*   **`add_cell`**: Adds a new cell to the currently loaded notebook.
    *   **Arguments**:
        *   `cell_type` (string): Cell type to add (`"code"` or `"markdown"`, case-insensitive).
        *   `content` (string): Source content for the new cell.
        *   `position` (integer, optional): Position to insert the cell (appends if `null`).
    *   **Returns**: (string) Success or failure message and current cell count.
*   **`edit_cell`**: Edits an existing cell in the currently loaded notebook.
    *   **Arguments**:
        *   `cell_index_or_position` (integer): 0-based position of the target cell.
        *   `content` (string): New content for the target cell.
        *   `cell_type` (string, optional): Optional new type (`"code"` or `"markdown"`).
    *   **Returns**: (string) Success or failure message and current cell count.
*   **`add_code_cell_to_loaded_notebook`** (deprecated): Backward-compatible wrapper for `add_cell("code", ...)`.
    *   **Arguments**:
        *   `code_content` (string): Source code for the new cell.
        *   `position` (integer, optional): Position to insert the cell (appends if `null`).
    *   **Returns**: (string) Success or failure message and current cell count.
*   **`add_markdown_cell_to_loaded_notebook`** (deprecated): Backward-compatible wrapper for `add_cell("markdown", ...)`.
    *   **Arguments**:
        *   `markdown_content` (string): Markdown content for the new cell.
        *   `position` (integer, optional): Position to insert the cell (appends if `null`).
    *   **Returns**: (string) Success or failure message and current cell count.
*   **`save_loaded_notebook`**: Saves the currently loaded notebook to a file.
    *   **Arguments**:
        *   `output_filepath` (string, optional): Absolute path to save the `.ipynb` file (must end with `.ipynb`). Saves to original path if `null`.
    *   **Returns**: (string) Success or failure message.

## Installation

### Using uv (recommended)

`jupyternotebook-mcp` is not currently published on PyPI.

Recommended: install it as a uv tool directly from this GitHub repository:

```bash
uv tool install jupyternotebook-mcp --from git+https://github.com/g0g5/jupyternotebook-mcp@main
```

Then run it with [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx jupyternotebook-mcp
```

If you have not installed it first (or want one-off execution), always pass `--from`:

```bash
uvx jupyternotebook-mcp --from git+https://github.com/g0g5/jupyternotebook-mcp@main
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

**Using uvx**
```json
{
  "mcpServers": {
    "jupyternotebook-mcp": {
      "command": "uvx",
      "args": ["jupyternotebook-mcp", "--from", "git+https://github.com/g0g5/jupyternotebook-mcp@main"]
    }
  }
}
```

### Configure for Zed

Add to your Zed `settings.json`:

**Using uvx**
```json
"context_servers": [
  "jupyternotebook-mcp": {
    "command": "uvx",
    "args": ["jupyternotebook-mcp", "--from", "git+https://github.com/g0g5/jupyternotebook-mcp@main"]
  }
],
```

### Configure for VS Code

For quick installation, use one of the one-click install buttons below...

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=jupyternotebook-mcp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22jupyternotebook-mcp%22%5D%7D) [![Install with UV in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UV-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=jupyternotebook-mcp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22jupyternotebook-mcp%22%5D%7D&quality=insiders)

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS) and typing `Preferences: Open User Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.
> Note that the `mcp` key is needed when using the `mcp.json` file.

**Using uvx**
```json
{
  "mcp": {
    "servers": {
      "jupyternotebook-mcp": {
        "command": "uvx",
        "args": ["jupyternotebook-mcp", "--from", "git+https://github.com/g0g5/jupyternotebook-mcp@main"]
      }
    }
  }
}
```

## Example Interactions

1.  **Load a notebook:**
    ```json
    {
      "name": "load_notebook",
      "arguments": {
        "filepath": "/path/to/your/notebook.ipynb"
      }
    }
    ```
    **Response:**
    ```json
    {
      "message": "Notebook /path/to/your/notebook.ipynb loaded successfully. Cell count: 10"
    }
    ```

2.  **Convert loaded notebook to plain text:**
    ```json
    {
      "name": "notebook_to_plain_text",
      "arguments": {}
    }
    ```
    **Response:**
    ```text
    # CELL 1 CODE
    print("Hello World")

    # CELL 2 MARKDOWN
    This is a markdown cell.
    ...
    ```

3.  **Convert plain text back to a notebook file:**
    ```json
    {
      "name": "plain_text_to_notebook_file",
      "arguments": {
        "plain_text_content": "# CELL 1 CODE\nprint(\"Hello Again\")\n\n# CELL 2 MARKDOWN\nAnother markdown cell.",
        "output_filepath": "/path/to/your/new_notebook.ipynb"
      }
    }
    ```
    **Response:**
    ```json
    {
      "message": "Notebook saved to /path/to/your/new_notebook.ipynb"
    }
    ```

## Debugging

You can use the MCP inspector to debug the server. For `uvx` installations:

```bash
npx @modelcontextprotocol/inspector uvx jupyternotebook-mcp --from git+https://github.com/g0g5/jupyternotebook-mcp@main
```

## Build

This package is typically installed with `uv tool install` or used directly with `uvx`. If you are developing the package, you can build it with `uv`.

```bash
uv build
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests for bug fixes, new features, or improvements to documentation.

## License

This project is licensed under the MIT License.
