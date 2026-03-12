notebook_to_plain_text -> read_notebook
plain_text_to_notebook_file -> X removed
new tool: save_notebook_markdown, to save the opened notebook as plain text markdown file as <notebook-name>.md in the same folder
new tool: markdown_to_notebook -> update opened notebook from plain text markdown
remove_cell -> explicitly tell the model that index won't change until the opened notebook is saved