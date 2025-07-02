# sosi_files_importer for Blender
Importer for SOSI files (containing 3D model data) used for geographical information in Norway. SOSI stands for Systematic Organization of Spatial Information. This format was first standardized around 1990 by *Statens Kartverk*, and is still in active use in Norway.

This is an addon for Blender to allow imports of SOSI files (with extension .sos). This addon is intended to handle the data normally contained in so-called 
"digital maps" available from Norwegian municipal og governmental services.

The add-on was originally written in C++ for Sketchup. Earlier releases used a Windows-only DLL for SOSI parsing but this has now been replaced by a cross-platform Python implementation.

The importer relies on the GDAL library to read SOSI files. Ensure the GDAL Python bindings are installed (for instance with `brew install gdal` on macOS, which works on Apple M‑series CPUs).

The *scripts/sosi_files_importer/* directory contains the Python sources for the add-on.

Currently the add-on has been tested with Blender 4.0 on Linux and macOS running on Apple M2 hardware.