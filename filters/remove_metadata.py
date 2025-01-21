import nbformat

def remove_metadata(notebook):
    for cell in notebook.cells:
        if 'metadata' in cell:
            cell['metadata'] = {}
    return notebook