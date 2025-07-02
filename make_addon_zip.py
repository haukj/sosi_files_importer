#!/usr/bin/env python3
"""Package the addon into a zip archive usable by Blender."""
import os
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ADDON_DIR = os.path.join(SCRIPT_DIR, 'scripts', 'sosi_files_importer')
OUTPUT_ZIP = os.path.join(SCRIPT_DIR, 'sosi_files_importer.zip')


def main():
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(ADDON_DIR):
            for fname in files:
                if fname.endswith('.pyc'):
                    continue
                path = os.path.join(root, fname)
                arcname = os.path.relpath(path, SCRIPT_DIR)
                zf.write(path, arcname)
    print(f'Created {OUTPUT_ZIP}')


if __name__ == '__main__':
    main()
