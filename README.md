# sosi_files_importer for Blender
Importer for SOSI files (containing 3D model data) used for geographical information in Norway. SOSI stands for Systematic Organization of Spatial Information. This format was first standardized around 1990 by *Statens Kartverk*, and is still in active use in Norway.

This is an addon for Blender to allow imports of SOSI files (with extension .sos). This addon is intended to handle the data normally contained in so-called 
"digital maps" available from Norwegian municipal og governmental services.

The add-on was originally written in C++ for Sketchup. Earlier releases used a Windows-only DLL for SOSI parsing but this has now been replaced by a cross-platform Python implementation.

The importer relies on the GDAL library to read SOSI files. Ensure the GDAL Python bindings are installed (for instance with `brew install gdal` on macOS, which works on Apple M‑series CPUs).

The *scripts/sosi_files_importer/* directory contains the Python sources for the add-on.

Currently the add-on has been tested with Blender 4.0 on Linux and macOS running on Apple M2 hardware.

![Example import](/images/ImportExample_0.png)

## Installation

While certainly possible, it is not recommended to install the addon using the sources directly. Instead, please use the packaged contents in the *Release page*. The packaged zip-file can be directly installed from the *Install...* button in the *Blender Preferences* dialog.

If building from source, run `python3 make_addon_zip.py` from the repository root. The script creates `sosi_files_importer.zip` which can be installed directly from the *Install...* button inside Blender.

## Usage

Initially, the importer has to be enabled via the *Edit/preferences* dialog. It can be found as *Import-Export: SosiImporter*.

![Demo import 0](/images/Importing_0.png)

Run the importer from the *File/Import/Import SOSI Data* menu item. A file selector will appear allowing you to choose one or more `.sos` files.

![Demo import 1](/images/Importing_1.png)

The selected SOSI files are parsed one by one and the geometry is added to the current scene. You may also bypass the dialog by setting the environment variable `SOSI_FILES` to a colon-separated list of file paths before starting Blender.

Please note that the importer uses standard Python logging mechanisms. One of these logging levels can be selected:
- DEBUG
- INFO
- WARNING
- ERROR

Default logging level after installation is INFO. The logging level can be changed by expanding the SosiImporter specific information from the *Blender Preferences* dialog.
Thus, it is a good idea to open the Blender *System Console* before doing any imports, as the console will display importing details while processing. Any problems occurring while importing should be indicated in the console window.

## Example .sos file

In order to verify that an add-on installation is working properly, the sources also include an example `.sos` file. A matching reference coordinate file from earlier releases is included but no longer required. The `.sos` file contains only rudimentary data, but is a perfectly valid SOSI file.

The example files can be found in the test_data directory:

```
test_data
|    SomeBorders.sos
|    SomeBorders_ref.txt
|  
└─── 
```

The result in Blender after import should look like this:

![TestFile import](/images/SomeBorders.png)

## File Format

The documentation for the SOSI format could certainly be better, but some documentation can be found via the link https://www.kartverket.no/geodataarbeid/standardisering/sosi-standarder2.

The format for the Reference file is pretty straight-forward. It simply takes two lines, one starting with E (for Easting) and one starting with N (for Northing). The float values after the letters are the corresponding coordinates values. The SOSI file data will be translated such that the Blender model origin will correspond to these coordinates.

```
E579843.71
N6635218.06
```

SOSI files ordered from public sources will come with UTM coordinates, which uses the notation Easting and Northing. It is beyond the scope of this document to further dive into this matter. https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system gives a good insight into the UTM system.
