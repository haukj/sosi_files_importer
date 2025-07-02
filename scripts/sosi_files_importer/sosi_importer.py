# -*- coding: utf-8 -*-
"""
Copyright © 2022 Jonny Normann Skålvik

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the “Software”), to deal 
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.

This file is part of SosiImporter, an addon to import SOSI files containing
3D model data into Blender.
"""

import bpy
import os
import sys
import numpy as np
import ctypes
from ctypes import wintypes
import logging
import platform
try:
    from osgeo import ogr  # noqa
    GDAL_AVAILABLE = True
except Exception:
    GDAL_AVAILABLE = False
from . import sosi_settings as soset
from . import sosi_log_helper as sologhlp
from . import sosi_geom_helper as sogeohlp

# -----------------------------------------------------------------------------

RES_SOSI_GENERAL_ERROR	    = 0x0001
RES_SOSI_DIMENSION_MISMATCH = 0x0010
RES_SOSI_LOOP_UNCLOSED      = 0x0100

#C = bpy.context
#D = bpy.data

# Parent object for all SOSI elements
#top_parent = None

# Determine if the code is running from within Blender
in_blender = True

try:
    import bpy
    in_blender = os.path.basename(bpy.app.binary_path or '').lower().startswith('blender')
except ModuleNotFoundError:
    in_blender = False   
#print('INFO: Blender environment:', in_blender)

if (in_blender == True):
    from . import sosi_datahelper as sodhlp    
    from . import blender_helper as bldhlp
    from bpy.types import AddonPreferences
    from bpy.props import EnumProperty
else:
    import sosi_datahelper as sodhlp    
    import blender_helper as bldhlp
    
#import sosi_datahelper as sodhlp
#from . import sosi_datahelper as sodhlp
#from sosi_importer import sosi_datahelper as sodhlp # from directory sosi_importer

#import blender_helper as bldhlp
#from sosi_importer import blender_helper as bldhlp # from directory sosi_importer

c_int = ctypes.c_int
c_int32 = ctypes.c_int32
c_double = ctypes.c_double
c_void_p = ctypes.c_void_p
c_char_p = ctypes.c_char_p

# -----------------------------------------------------------------------------

class SosiImporterPreferences(AddonPreferences):
    
    bl_idname = __package__
    
    def update_log_level(self, context):
        logging.info("Setting log level to %s", self.log_level)
        #logging.setLevel(self.log_level)
        #print('-->', self.log_level)
        return
    
    # Debug levels:
    # CRITICAL  50
    # ERROR 	40
    # WARNING 	30
    # INFO      20
    # DEBUG 	10
    # NOTSET 	0
    
    log_levels = [
        ('DEBUG', "Debug", "Debug output", 0),
        ('INFO', "Information", "Informational output", 1),
        ('WARNING', "Warnings", "Show only warnings and errors", 2),
        ('ERROR', "Errors", "Show errors only", 3)
        ]

    log_level: EnumProperty(
        name = "Logging level",
        description = "Minimum events severity level to output. All more severe messages will be logged as well.",
        items = log_levels,
        update = update_log_level,  # update method when changing
        default = 'INFO')
    
#    def update_test_xenums(self, context):
#        print("Hey")
#        return
#    
#    test_xenums = [
#        ('ONE', "One", "eqwe"),
#        ('TWO', "Two", "sdaasd"),
#        ('THREE', "Three", "dsfasdf")
#        ]
#    
#    test_xenum: EnumProperty(
#        name = "Some name",
#        description = "Some description",
#        items = test_xenums,
#        update = update_test_xenums,
#        default = 'THREE' 
#        )
   
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "log_level")
#        layout.prop(self, "test_xenum")

# -----------------------------------------------------------------------------

def coord_array_to_list(ndims, ncoords, ary):
    coordList = []
    if (ndims == 2):
        for i in range(ncoords):
            coordList.append((ary[i * 2], ary[i * 2 + 1], 0.0))
    else: # ndims == 3
        for i in range(ncoords):
            coordList.append((ary[i * 3], ary[i * 3 + 1], ary[i * 3 + 2]))
    return coordList

# -----------------------------------------------------------------------------

def get_full_path(rel_path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    head_path, tail_path = os.path.split(dir_path)
    return os.path.join(head_path, rel_path)

# -----------------------------------------------------------------------------

def free_library(handle):
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    #kernel32.FreeLibrary.argtypes = [ctypes.wintypes.HMODULE]
    #kernel32.FreeLibrary.restype = ctypes.wintypes.BOOL
    kernel32.FreeLibrary.argtypes = [wintypes.HMODULE]
    kernel32.FreeLibrary.restype = wintypes.BOOL
    kernel32.FreeLibrary(handle)

# -----------------------------------------------------------------------------

# Function will be called per sosi object and return ptr to object name, ptr to coordinate array 
def my_cb_func(id, objrefnum, sosires, pobjname, ndims, ncoords, pcoord_ary, pfilename):
	
    #global top_parent
    #print('PAR2 before:', top_parent)
    
    sosi_parent_name = "SOSI_Parent"  
    top_parent = bldhlp.get_or_create_SOSI_parent_object(sosi_parent_name)
	
    objname = pobjname.decode('utf-8')  # Interpret the byte array as utf-8
    #print(objname)
    # NUMPY copy
    a = np.fromiter(pcoord_ary, dtype=np.double, count=ndims * ncoords)
    coord_list = coord_array_to_list(ndims, ncoords, a)
    #print("A", coord_list)
    #bpy.ops.object.mode_set(mode = 'OBJECT')
    filename = pfilename.decode('utf8')
    #print(filename) # pfilename is already utf8
    coll = bldhlp.Collection.get_or_create_linked_subcollection_by_name('SOSI', filename)
    
    if (sodhlp.SosiObjId(id) == sodhlp.SosiObjId.PUNKT):
        ob = bldhlp.Mesh.point_cloud(objname, coord_list)
        
        if bldhlp.get_mesh_obj_named(objname) != None:
            ob = bldhlp.mesh_obj_join_existing(objname, ob)
            #print('  Joined', ob.data)
            logging.debug('  Joined', ob.data)
        else:
            ob.parent = top_parent
            #bpy.context.collection.objects.link(ob)
            coll.objects.link(ob)
            
        bldhlp.lock_obj_to_parent(ob)
        #print('PUNKT {}: Res= 0x{:x} NoOfCoords= {}'.format(objrefnum, sosires, ncoords))
        logging.info('PUNKT {}: Res= 0x{:x} NoOfCoords= {}'.format(objrefnum, sosires, ncoords))
    elif (sodhlp.SosiObjId(id) == sodhlp.SosiObjId.KURVE):
        #print("A", coord_list)
        edg_list = sodhlp.points_to_edglist(coord_list)
        #print("B", edg_list)
        ob = bldhlp.Mesh.point_cloud(objname, coord_list, edg_list)
        
        if bldhlp.get_mesh_obj_named(objname) != None:
            ob = bldhlp.mesh_obj_join_existing(objname, ob)
            #print('  Joined', ob.data)
            logging.debug('  Joined', ob.data)
        else:
            ob.parent = top_parent
            #bpy.context.collection.objects.link(ob)
            coll.objects.link(ob)
            
        bldhlp.lock_obj_to_parent(ob)
        #print('KURVE {}: Res= 0x{:x} NoOfCoords= {}'.format(objrefnum, sosires, ncoords))
        logging.info('KURVE {}: Res= 0x{:x} NoOfCoords= {}'.format(objrefnum, sosires, ncoords))
    elif (sodhlp.SosiObjId(id) == sodhlp.SosiObjId.FLATE):
        #print("A", coord_list)
        edg_list = sodhlp.points_to_edglist(coord_list)
        ob = bldhlp.Mesh.point_cloud(objname, coord_list, edg_list)
        
        if bldhlp.get_mesh_obj_named(objname) != None:
            ob = bldhlp.mesh_obj_join_existing(objname, ob)
            #print('  Joined', ob.data)
            logging.debug('  Joined', ob.data)
        else:
            ob.parent = top_parent
            #ob = bldhlp.Mesh.point_cloud(filename, coord_list, edg_list)
            #bpy.context.collection.objects.link(ob)
            coll.objects.link(ob)
            
        bldhlp.lock_obj_to_parent(ob)
        #print ('FLATE {}: Res= 0x{:x} NoOfCoords= {}'.format(objrefnum, sosires, ncoords))
        logging.info('FLATE {}: Res= 0x{:x} NoOfCoords= {}'.format(objrefnum, sosires, ncoords))
        if (sosires & RES_SOSI_DIMENSION_MISMATCH):
            print('  WARNING: Dimension mismatch in FLATE elements, drawing might be strange.')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.edge_face_add() # Make the ngon
        #bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY') # Triangulate
        bpy.ops.object.mode_set(mode = 'OBJECT')
    elif (sodhlp.SosiObjId(id) == sodhlp.SosiObjId.BUEP):
        num_segs = 8
        arc_seg_pts = sogeohlp.arc_pts_segments_3D(coord_list, num_segs)
        edg_list = sodhlp.points_to_edglist(arc_seg_pts)
        ob = bldhlp.Mesh.point_cloud(objname, arc_seg_pts, edg_list)
        
        if bldhlp.get_mesh_obj_named(objname) != None:
            ob = bldhlp.mesh_obj_join_existing(objname, ob)
            #print('  Joined', ob.data)
            logging.debug('  Joined', ob.data)
        else:
            ob.parent = top_parent
            #bpy.context.collection.objects.link(ob)
            coll.objects.link(ob)
            
        bldhlp.lock_obj_to_parent(ob)
        #print('BUEP {}: Res= 0x{:x} NoOfCoords= {}'.format(objrefnum, sosires, ncoords))
        logging.info('BUEP {}: Res= 0x{:x} NoOfCoords= {}'.format(objrefnum, sosires, ncoords))
        
    return 0

# -----------------------------------------------------------------------------

def do_imports():
    
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    
    #logger = sologhlp.get_logger(soset.ACT_LOG_LEVEL)
    logger = sologhlp.get_logger(addon_prefs.log_level)
    
    global top_parent
    top_parent = None
    
    if soset.USE_DEBUG_DLL_PATH == True:
        dll_path = soset.DEBUG_DLL_PATH
    else:
        rel_path = soset.REL_DLL_PATH
        dll_path = get_full_path(rel_path)

    use_dll = platform.system() == 'Windows' and os.path.exists(dll_path)

    #Prototype callback
    callback_type = ctypes.CFUNCTYPE(c_int, c_int, c_int, c_int, c_char_p, c_int, c_int, ctypes.POINTER(c_double), c_char_p)
    my_callback = callback_type(my_cb_func)  # Use a variable to avoid garbage collection

    if use_dll:
        my_dll = ctypes.WinDLL(dll_path)

        # Prototype get_SosiInputObjects()
        my_dll.get_SosiInputObjects.argtypes = [ctypes.POINTER(c_double), ctypes.POINTER(c_double), ctypes.POINTER(c_double), ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_double]
        my_dll.get_SosiInputObjects.restype = c_int

        #Prototype process_SosiFiles()
        my_dll.process_SosiFiles.argtypes = [c_int, c_void_p]
        my_dll.process_SosiFiles.restype = c_int
    
    bldscale = 1.0  # bldhlp.LocalUnits.scene_unit_factor() # STRANGE??? Blender takes numbers as m always???
    #bldhlp.setMyEnvironment()   # TEMPORARY to set my local environment

    peasting = (ctypes.c_double)()
    pnorthing = (ctypes.c_double)()
    punity = (ctypes.c_double)()
    clip_end = bldhlp.SceneSettings.get_clip_end()
    unit_system = bldhlp.UnitSettings.scene_unit_system_get()
    unit_length = bldhlp.UnitSettings.scene_unit_length_get()
    unit_scale = bldhlp.UnitSettings.scene_unit_scale_get()

    if use_dll:
        nfiles = my_dll.get_SosiInputObjects(peasting, pnorthing, punity, bldscale, clip_end, unit_system, unit_length, unit_scale)
        if nfiles > 0:
            my_dll.process_SosiFiles(nfiles, my_callback)
        lib_handle = my_dll._handle
        free_library(lib_handle)
    else:
        if not GDAL_AVAILABLE:
            logging.error('GDAL Python bindings not available')
            return 0
        from . import sosi_gdal_parser
        env_files = os.environ.get('SOSI_FILES')
        if env_files:
            file_list = env_files.split(os.pathsep)
        else:
            pkg_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            file_list = [os.path.join(pkg_dir, 'test_data', 'SomeBorders.sos')]
        nfiles = sosi_gdal_parser.process_sosi_files(file_list, my_cb_func)

    return nfiles
