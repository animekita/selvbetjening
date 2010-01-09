def add_contrib_to_python_path():
    import sys
    import os

    contrib_path = os.path.dirname(__file__)

    for entry in os.listdir(contrib_path):
        entry_path = os.path.join(contrib_path, entry)

        if os.path.isdir(entry_path):
            sys.path.append(entry_path)