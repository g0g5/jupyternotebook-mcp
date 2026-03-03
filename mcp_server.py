import os
from mcp.server.fastmcp import FastMCP  # Add MCP import
from notebookllm import Notebook


mcp = FastMCP("ipynb-mcp")

# Store the loaded notebook in memory.
loaded_notebook: Notebook | None = None
loaded_notebook_path: str | None = None
cell_index: dict[str, list[int]] | None = None


def _build_cell_index(notebook: Notebook) -> dict[str, list[int]]:
    index: dict[str, list[int]] = {"all": [], "code": [], "markdown": []}
    for position, cell in enumerate(notebook.cells):
        index["all"].append(position)
        cell_type = getattr(cell, "cell_type", None)
        if cell_type == "code":
            index["code"].append(position)
        elif cell_type == "markdown":
            index["markdown"].append(position)
    return index


def _refresh_cell_index() -> None:
    global cell_index, loaded_notebook
    if not loaded_notebook:
        cell_index = None
        return
    cell_index = _build_cell_index(loaded_notebook)


def _require_loaded_notebook() -> str | None:
    if not loaded_notebook:
        return "Error: No notebook is currently loaded. Use load_notebook() first."
    return None


def _normalize_cell_type(cell_type: str) -> str | None:
    normalized_type = cell_type.strip().lower()
    if normalized_type not in ("code", "markdown"):
        return None
    return normalized_type


def _validate_insert_position(position: int | None, total_cells: int) -> str | None:
    if position is None:
        return None
    if isinstance(position, bool) or not isinstance(position, int):
        return "Error: Invalid position type. Position must be an integer."
    if position < 0 or position > total_cells:
        return (
            f"Error: Invalid position {position}. Allowed range is 0 to {total_cells}."
        )
    return None


@mcp.tool()
def load_notebook(filepath: str) -> str:
    """Loads a .ipynb file into memory. Prepares notebook for efficient, cost-effective text-based operations with LLMs.
    Args:
        filepath (str): The absolute path to the .ipynb file.
    Returns:
        str: A message indicating success or failure, including cell count for context.
    """
    global loaded_notebook, loaded_notebook_path, cell_index
    try:
        if not os.path.exists(filepath):
            loaded_notebook = None
            loaded_notebook_path = None
            cell_index = None
            return f"Error: File not found at {filepath}"
        if not filepath.endswith(".ipynb"):
            loaded_notebook = None
            loaded_notebook_path = None
            cell_index = None
            return "Error: Filepath must be for a .ipynb file."
        loaded_notebook = Notebook(filepath)
        loaded_notebook_path = filepath
        _refresh_cell_index()
        return f"Successfully loaded notebook: {filepath}. It has {len(loaded_notebook.cells)} cells. Ready for efficient text conversion."
    except Exception as e:
        loaded_notebook = None
        loaded_notebook_path = None
        cell_index = None
        return f"Error loading notebook: {str(e)}"


@mcp.tool()
def notebook_to_plain_text(input_filepath: str | None = None) -> str:
    """Converts a .ipynb file to a simplified plain text representation, stripping metadata to save tokens and reduce LLM processing costs and time.
    If input_filepath is provided, it loads and converts that file.
    Otherwise, it efficiently converts the currently loaded notebook.

    Args:
        input_filepath (str, optional): The absolute path to the .ipynb file for on-the-fly conversion.
    Returns:
        str: The token-efficient plain text representation of the notebook or an error message.
    """
    global loaded_notebook
    try:
        notebook_to_convert = None
        status_prefix = ""
        if input_filepath:
            if not os.path.exists(input_filepath):
                return f"Error: Input file not found at {input_filepath}"
            if not input_filepath.endswith(".ipynb"):
                return "Error: Input filepath must be for a .ipynb file."
            notebook_to_convert = Notebook(input_filepath)
            status_prefix = f"Converted notebook from {input_filepath}."
        elif loaded_notebook:
            notebook_to_convert = loaded_notebook
            status_prefix = "Converted currently loaded notebook."
        else:
            return "Error: No notebook loaded and no input_filepath provided. Use load_notebook() or provide input_filepath for efficient conversion."

        plain_text = notebook_to_convert.to_plain_text()
        return f"{status_prefix} Plain text (optimized for token and cost savings):\n\n{plain_text}"
    except Exception as e:
        return f"Error converting notebook to plain text: {str(e)}"


@mcp.tool()
def plain_text_to_notebook_file(plain_text_content: str, output_filepath: str) -> str:
    """Converts token-efficient plain text content (with special markers) back to a .ipynb file and saves it. Enables cost-effective round-trip editing with LLMs.

    Args:
        plain_text_content (str): The plain text content (optimized for LLMs) to convert.
        output_filepath (str): The absolute path where the .ipynb file should be saved. Must end with '.ipynb'.
    Returns:
        str: A message indicating success or failure of the save operation.
    """
    global loaded_notebook, loaded_notebook_path
    try:
        if not output_filepath.endswith(".ipynb"):
            return "Error: Output filepath must end with .ipynb"

        # Ensure the directory for the output file exists
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        new_notebook = Notebook.from_plain_text(plain_text_content)
        new_notebook.save(output_filepath)
        # Update the loaded notebook to the one just created and saved
        loaded_notebook = new_notebook
        loaded_notebook_path = output_filepath
        _refresh_cell_index()
        return f"Successfully converted plain text to notebook and saved to: {output_filepath}. It is now the active notebook, enabling further efficient operations."
    except Exception as e:
        return f"Error converting plain text to notebook: {str(e)}"


@mcp.tool()
def add_cell(cell_type: str, content: str, position: int | None = None) -> str:
    """Adds a new cell to the currently loaded notebook.

    Args:
        cell_type (str): The cell type to add (code or markdown).
        content (str): The source content for the new cell.
        position (int, optional): The position at which to insert the cell. Appends if None for quick addition.
    Returns:
        str: A message indicating success or failure and current cell count.
    """
    global loaded_notebook
    loaded_error = _require_loaded_notebook()
    if loaded_error:
        return loaded_error
    notebook = loaded_notebook
    if notebook is None:
        return "Error: No notebook is currently loaded. Use load_notebook() first."

    normalized_cell_type = _normalize_cell_type(cell_type)
    if not normalized_cell_type:
        return f"Error: Invalid cell_type '{cell_type}'. Allowed: code, markdown."

    position_error = _validate_insert_position(position, len(notebook.cells))
    if position_error:
        return position_error

    try:
        if normalized_cell_type == "code":
            if position is None:
                notebook.add_code_cell(source=content)
            else:
                notebook.add_code_cell(source=content, position=position)
        else:
            if position is None:
                notebook.add_markdown_cell(source=content)
            else:
                notebook.add_markdown_cell(source=content, position=position)
        _refresh_cell_index()
        inserted_position = (
            position if position is not None else len(notebook.cells) - 1
        )
        return (
            f"Added {normalized_cell_type} cell at position {inserted_position}. "
            f"Loaded notebook now has {len(notebook.cells)} cells."
        )
    except Exception as e:
        return f"Error: Failed to add {normalized_cell_type} cell: {str(e)}"


@mcp.tool()
def edit_cell(
    cell_index_or_position: int, content: str, cell_type: str | None = None
) -> str:
    """Edits an existing cell in the currently loaded notebook.

    Args:
        cell_index_or_position (int): The 0-based position of the cell to edit.
        content (str): The new source content for the target cell.
        cell_type (str, optional): Optional new cell type (code or markdown).
    Returns:
        str: A message indicating success or failure and current cell count.
    """
    global loaded_notebook
    loaded_error = _require_loaded_notebook()
    if loaded_error:
        return loaded_error
    notebook = loaded_notebook
    if notebook is None:
        return "Error: No notebook is currently loaded. Use load_notebook() first."

    if isinstance(cell_index_or_position, bool) or not isinstance(
        cell_index_or_position, int
    ):
        return "Error: Invalid cell index. It must be an integer."

    total_cells_before = len(notebook.cells)
    if total_cells_before == 0:
        return "Error: Cannot edit cell 0 because the notebook has no cells."
    if cell_index_or_position < 0 or cell_index_or_position >= total_cells_before:
        return (
            f"Error: Cell index {cell_index_or_position} is out of range. "
            f"Allowed range is 0 to {total_cells_before - 1}."
        )

    requested_cell_type: str | None = None
    if cell_type is not None:
        requested_cell_type = _normalize_cell_type(cell_type)
        if not requested_cell_type:
            return f"Error: Invalid cell_type '{cell_type}'. Allowed: code, markdown."

    try:
        if requested_cell_type is None:
            notebook.edit_cell(index=cell_index_or_position, source=content)
        else:
            notebook.edit_cell(
                index=cell_index_or_position,
                source=content,
                cell_type=requested_cell_type,
            )
        total_cells_after = len(notebook.cells)
        if total_cells_before != total_cells_after:
            return "Error: Cell edit changed notebook cell count unexpectedly."

        _refresh_cell_index()
        edited_cell_type = getattr(
            notebook.cells[cell_index_or_position], "cell_type", "unknown"
        )
        return (
            f"Edited {edited_cell_type} cell at position {cell_index_or_position}. "
            f"Loaded notebook now has {total_cells_after} cells."
        )
    except Exception as e:
        return (
            f"Error: Failed to edit cell at position {cell_index_or_position}: {str(e)}"
        )


@mcp.tool()
def remove_cell(cell_index_or_position: int) -> str:
    """Removes a cell from the currently loaded notebook.

    Args:
        cell_index_or_position (int): The 0-based position of the cell to remove.
    Returns:
        str: A message indicating success or failure and current cell count.
    """
    global loaded_notebook
    loaded_error = _require_loaded_notebook()
    if loaded_error:
        return loaded_error
    notebook = loaded_notebook
    if notebook is None:
        return "Error: No notebook is currently loaded. Use load_notebook() first."

    if isinstance(cell_index_or_position, bool) or not isinstance(
        cell_index_or_position, int
    ):
        return "Error: Invalid cell index. It must be an integer."

    total_cells_before = len(notebook.cells)
    if total_cells_before == 0:
        return "Error: Cannot remove cell 0 because the notebook has no cells."
    if cell_index_or_position < 0 or cell_index_or_position >= total_cells_before:
        return (
            f"Error: Cell index {cell_index_or_position} is out of range. "
            f"Allowed range is 0 to {total_cells_before - 1}."
        )

    try:
        removed_cell_type = getattr(
            notebook.cells[cell_index_or_position], "cell_type", "unknown"
        )
        del notebook.cells[cell_index_or_position]
        _refresh_cell_index()
        total_cells_after = len(notebook.cells)
        return (
            f"Removed {removed_cell_type} cell at position {cell_index_or_position}. "
            f"Loaded notebook now has {total_cells_after} cells."
        )
    except Exception as e:
        return f"Error: Failed to remove cell at position {cell_index_or_position}: {str(e)}"


@mcp.tool()
def save_loaded_notebook(output_filepath: str | None = None) -> str:
    """Saves the currently loaded notebook to a file. Efficiently persists changes made in memory.
    If output_filepath is provided, saves to that path.
    Otherwise, saves to its original path, ensuring data integrity with minimal overhead.

    Args:
        output_filepath (str, optional): The absolute path to save the .ipynb file. Must end with '.ipynb'.
    Returns:
        str: A message indicating success or failure of the save operation.
    """
    global loaded_notebook, loaded_notebook_path
    if not loaded_notebook:
        return "Error: No notebook is currently loaded. Use load_notebook() first to enable saving."
    try:
        save_path = output_filepath
        if save_path:
            if not save_path.endswith(".ipynb"):
                return "Error: Output filepath must end with .ipynb"
            # Ensure the directory for the output file exists
            output_dir = os.path.dirname(save_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
        elif loaded_notebook_path:
            save_path = loaded_notebook_path
        else:
            return "Error: No output path specified and the notebook was not loaded from a file. Cannot efficiently save."

        loaded_notebook.save(save_path)
        if (
            output_filepath
        ):  # If a new path was provided, update the loaded_notebook_path
            loaded_notebook_path = output_filepath
        return f"Successfully and efficiently saved notebook to: {save_path}"
    except Exception as e:
        return f"Error saving notebook: {str(e)}"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
