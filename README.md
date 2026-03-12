# Jupyter Notebook MCP

A Model Context Protocol server for working with Jupyter Notebooks (`.ipynb` files) in a way that is efficient for Large Language Models (LLMs). It reads and writes notebooks in the existing `notebookllm` plain-text markdown format (`# %% [markdown]`, `# %% [code]`, and similar cell markers) so notebook content can be reviewed and replaced without immediately saving the `.ipynb` file.

## Available Tools

*   **`load_notebook`**: Loads a `.ipynb` file into memory.
    *   **Arguments**:
        *   `filepath` (string): The absolute path to the `.ipynb` file.
    *   **Returns**: (string) Success or failure message, including cell count.
*   **`read_notebook`**: Reads a `.ipynb` file (loaded or from path) as `notebookllm` plain-text markdown.
    *   **Arguments**:
        *   `input_filepath` (string, optional): Absolute path to the `.ipynb` file for on-the-fly conversion.
    *   **Returns**: (string) Notebook plain-text markdown or an error message.
*   **`save_notebook_markdown`**: Saves the currently loaded notebook as a sibling `.md` file using the same basename.
    *   **Arguments**:
        *   None.
    *   **Returns**: (string) Success or failure message with the resolved markdown path.
*   **`markdown_to_notebook`**: Replaces the currently loaded in-memory notebook from `notebookllm` plain-text markdown.
    *   **Arguments**:
        *   `markdown_content` (string): Plain-text markdown content in the current `notebookllm` cell format.
    *   **Returns**: (string) Success or failure message and resulting cell count. This updates memory only; use `save_loaded_notebook` to persist the `.ipynb` file.
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
*   **`remove_cell`**: Removes a cell from the currently loaded notebook.
    *   **Arguments**:
        *   `cell_index_or_position` (integer): 0-based position of the target cell.
    *   **Returns**: (string) Success or failure message and current cell count. Responses also state that, for the opened notebook, cell indices should be treated as unchanged until `save_loaded_notebook` is called.
*   **`save_loaded_notebook`**: Saves the currently loaded notebook to a file.
    *   **Arguments**:
        *   `output_filepath` (string, optional): Absolute path to save the `.ipynb` file (must end with `.ipynb`). Saves to original path if `null`.
    *   **Returns**: (string) Success or failure message.

## Installation

### Using uv (recommended)

`ipynb-mcp` is not currently published on PyPI.

Recommended: install it as a uv tool directly from this GitHub repository:

```bash
uv tool install ipynb-mcp --from git+https://github.com/g0g5/jupyternotebook-mcp@main
```

Then run it with [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx ipynb-mcp
```

If you have not installed it first (or want one-off execution), always pass `--from`:

```bash
uvx ipynb-mcp --from git+https://github.com/g0g5/jupyternotebook-mcp@main
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

**Using uvx**
```json
{
  "mcpServers": {
    "ipynb-mcp": {
      "command": "uvx",
      "args": ["ipynb-mcp", "--from", "git+https://github.com/g0g5/jupyternotebook-mcp@main"]
    }
  }
}
```

### Configure for Zed

Add to your Zed `settings.json`:

**Using uvx**
```json
"context_servers": [
  "ipynb-mcp": {
    "command": "uvx",
    "args": ["ipynb-mcp", "--from", "git+https://github.com/g0g5/jupyternotebook-mcp@main"]
  }
],
```

### Configure for VS Code

For quick installation, use one of the one-click install buttons below...

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=ipynb-mcp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22ipynb-mcp%22%5D%7D) [![Install with UV in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UV-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=ipynb-mcp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22ipynb-mcp%22%5D%7D&quality=insiders)

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS) and typing `Preferences: Open User Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.
> Note that the `mcp` key is needed when using the `mcp.json` file.

**Using uvx**
```json
{
  "mcp": {
    "servers": {
      "ipynb-mcp": {
        "command": "uvx",
        "args": ["ipynb-mcp", "--from", "git+https://github.com/g0g5/jupyternotebook-mcp@main"]
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

2.  **Read the loaded notebook as plain-text markdown:**
    ```json
    {
      "name": "read_notebook",
      "arguments": {}
    }
    ```
    **Response:**
    ```text
    Read markdown for the currently loaded notebook. Notebook plain-text markdown:

    # %% [code]
    print("Hello World")

    # %% [markdown]
    This is a markdown cell.
    ...
    ```

3.  **Save the loaded notebook as sibling markdown:**
    ```json
    {
      "name": "save_notebook_markdown",
      "arguments": {}
    }
    ```
    **Response:**
    ```json
    {
      "message": "Successfully saved notebook markdown to: /path/to/your/notebook.md"
    }
    ```

4.  **Replace the loaded notebook from edited markdown:**
    ```json
    {
      "name": "markdown_to_notebook",
      "arguments": {
        "markdown_content": "# %% [code]\nprint(\"Hello Again\")\n\n# %% [markdown]\nAnother markdown cell."
      }
    }
    ```
    **Response:**
    ```json
    {
      "message": "Successfully replaced the loaded notebook in memory from markdown. Loaded notebook now has 2 cells. Use save_loaded_notebook() to persist the updated .ipynb file."
    }
    ```

5.  **Remove a cell while keeping index references stable until save:**
    ```json
    {
      "name": "remove_cell",
      "arguments": {
        "cell_index_or_position": 1
      }
    }
    ```
    **Response:**
    ```json
    {
      "message": "Removed markdown cell at position 1. Loaded notebook now has 1 cells. For this opened notebook, treat cell indices as unchanged until save_loaded_notebook() is called."
    }
    ```

## Debugging

You can use the MCP inspector to debug the server. For `uvx` installations:

```bash
npx @modelcontextprotocol/inspector uvx ipynb-mcp --from git+https://github.com/g0g5/jupyternotebook-mcp@main
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
