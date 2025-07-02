"""Simple SOSI parser using GDAL as a fallback for non-Windows systems."""

import os
from osgeo import ogr
from . import sosi_datahelper as sodhlp


def process_sosi_files(file_paths, callback):
    """Process SOSI files using GDAL and invoke callback for each feature.

    Args:
        file_paths (list[str]): list of SOSI files to parse
        callback (callable): function called for each geometry
    Returns:
        int: number of files processed
    """
    count = 0
    for path in file_paths:
        ds = ogr.Open(path)
        if ds is None:
            continue
        layer = ds.GetLayer(0)
        for idx, feature in enumerate(layer):
            geom = feature.geometry()
            if geom is None:
                continue
            gname = geom.GetGeometryName().upper()
            if gname in ("POINT", "MULTIPOINT"):
                obj_id = sodhlp.SosiObjId.PUNKT.value
            elif gname in ("LINESTRING", "MULTILINESTRING"):
                obj_id = sodhlp.SosiObjId.KURVE.value
            elif gname in ("POLYGON", "MULTIPOLYGON"):
                obj_id = sodhlp.SosiObjId.FLATE.value
            else:
                continue
            coords = [geom.GetPoint(i) for i in range(geom.GetPointCount())]
            flat = [c for pt in coords for c in (pt[0], pt[1], pt[2])]
            name = feature.GetField("objekttypenavn") or f"feat_{idx}"
            callback(
                obj_id,
                idx,
                0,
                name.encode("utf-8"),
                3,
                len(coords),
                flat,
                os.path.basename(path).encode("utf-8"),
            )
        count += 1
    return count
