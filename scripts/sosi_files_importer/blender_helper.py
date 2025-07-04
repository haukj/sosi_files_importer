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
import bmesh

# -----------------------------------------------------------------------------

UNIT_SYSTEM_NONE = 0
UNIT_SYSTEM_METRIC = 1
UNIT_SYSTEM_IMPERIAL = 2
 
UNIT_LENGTH_ADAPTIVE = 0
UNIT_LENGTH_MICROMETERS = 1
UNIT_LENGTH_MILLIMETERS = 2
UNIT_LENGTH_CENTIMETERS = 3
UNIT_LENGTH_METERS = 4
UNIT_LENGTH_KILOMETERS = 5
UNIT_LENGTH_THOU = 6	# aka mil
UNIT_LENGTH_INCHES = 7
UNIT_LENGTH_FEET = 8
UNIT_LENGTH_MILES = 9
 
# -----------------------------------------------------------------------------
 
class UnitSettings():

#    # Units used by blender
#    unit_factors = {
#        'MICROMETERS' : 1000000,
#        'MILLIMETERS' : 1000,
#        'CENTIMETERS' : 100,
#        'METERS' : 1,
#        'KILOMETERS' : 0.001
#        }
        
    unit_system = {
        'NONE' : UNIT_SYSTEM_NONE,
        'METRIC' : UNIT_SYSTEM_METRIC,
        'IMPERIAL' : UNIT_SYSTEM_IMPERIAL
    }
    unit_length = {
        'ADAPTIVE' : UNIT_LENGTH_ADAPTIVE,
        'MICROMETERS' : UNIT_LENGTH_MICROMETERS,
        'MILLIMETERS' : UNIT_LENGTH_MILLIMETERS,
        'CENTIMETERS' : UNIT_LENGTH_CENTIMETERS,
        'METERS' : UNIT_LENGTH_METERS,
        'KILOMETERS' : UNIT_LENGTH_KILOMETERS,
        'THOU' : UNIT_LENGTH_THOU,
        'INCHES' : UNIT_LENGTH_INCHES,
        'FEET' : UNIT_LENGTH_FEET,
        'MILES' : UNIT_LENGTH_MILES
    }

#    @staticmethod
#    def scene_unit_factor():
#        # Get the scale factor to apply to the SOSI meter based numbers
#        f = LocalUnits.unit_factors.get(bpy.context.scene.unit_settings.length_unit, None)
#        if (f == None):
#            return 1    # FIXME
#        return f / bpy.context.scene.unit_settings.scale_length
        
    @staticmethod
    def scene_unit_system_get():
        v = UnitSettings.unit_system.get(bpy.context.scene.unit_settings.system, None)
        return v
				
    @staticmethod
    def scene_unit_length_get():
        v = UnitSettings.unit_length.get(bpy.context.scene.unit_settings.length_unit, None)
        return v
				
    @staticmethod
    def scene_unit_scale_get():
        return bpy.context.scene.unit_settings.scale_length

# -----------------------------------------------------------------------------

class Mesh():
    
    @staticmethod
    def point_cloud(ob_name, coords, edges = [], faces = []):
        """Create point cloud object based on given coordinates and name.

        Keyword arguments:
        ob_name -- new object name
        coords -- float triplets eg: [(-1.0, 1.0, 0.0), (-1.0, -1.0, 0.0)]
        """
        #print(ob_name)
        #print(coords)
        #if (len(edges) > 0):
        #    print(edges)
        
        # Create new mesh and a new object
        mesh = bpy.data.meshes.new(ob_name)
        obj = bpy.data.objects.new(ob_name, mesh)
        
        mesh.from_pydata(coords, edges, faces)
        mesh.update()
        
        return obj
        
# -----------------------------------------------------------------------------
        
class Collection():

    @staticmethod
    def get_or_create_linked_collection_by_name(coll_name):
        coll = bpy.data.collections.get(coll_name)
        # if it doesn't exist create it
        if coll is None:
            coll = bpy.data.collections.new(coll_name)
            #print('Main collection created')
            bpy.context.scene.collection.children.link(coll )
        return coll

    @staticmethod
    def get_or_create_linked_subcollection_by_name(mcoll_name, scoll_name):
        mcoll = Collection.get_or_create_linked_collection_by_name(mcoll_name)
        scoll = bpy.data.collections.get(scoll_name)
        if scoll is None:
            scoll = bpy.data.collections.new(scoll_name)
            #print('Sub collection created')
            mcoll.children.link(scoll)
        return scoll

    @staticmethod
    def get_or_create_linked_sub2collection_by_name(mcoll_name, scoll1_name, scoll2_name):
        scoll1 = Collection.get_or_create_linked_subcollection_by_name(mcoll_name, scoll1_name)
        scoll2 = bpy.data.collections.get(scoll2_name)
        if scoll2 is None:
            scoll2 = bpy.data.collections.new(scoll2_name)
            #print('Sub2 collection created')
            scoll1.children.link(scoll2)
        return scoll2
    
# -----------------------------------------------------------------------------
    
class SceneSettings():
                
    @staticmethod
    def v3d_area_idx():
        res = None
        for i, a in enumerate(bpy.context.screen.areas):
            #print(i, a.type)
            if a.type == 'VIEW_3D':
                res = i
        return res
    
    @staticmethod
    def get_clip_end():
        idx = SceneSettings.v3d_area_idx()
        if (idx == None):
            return idx
        v3d_area = bpy.context.screen.areas[idx]
        space_data = v3d_area.spaces.active
        return space_data.clip_end

    @staticmethod
    def set_clip_end(v):
        idx = SceneSettings.v3d_area_idx()
        if (idx == None):
            return idx
        v3d_area = bpy.context.screen.areas[idx]
        space_data = v3d_area.spaces.active
        space_data.clip_end = v
        return space_data.clip_end
    
    @staticmethod
    def set_shading():
        idx = SceneSettings.v3d_area_idx()
        if (idx == None):
            return idx
        v3d_area = bpy.context.screen.areas[idx]
        space_data = v3d_area.spaces.active
        space_data.shading.type = 'RENDERED'
        
# -----------------------------------------------------------------------------

def get_or_create_SOSI_parent_object(sosi_parent_name):
    top_parent = bpy.data.objects.get(sosi_parent_name)
    if top_parent == None:
        top_parent = bpy.data.objects.new(sosi_parent_name, None)
        top_parent.empty_display_size = 1
        #top_parent.empty_display_type = 'PLAIN_AXES'
        top_parent.empty_display_type = 'SPHERE'
        bpy.context.scene.collection.objects.link(top_parent)
#           logging.debug(' SOSI_Parent:', top_parent)
    return top_parent
    
# -----------------------------------------------------------------------------
        
def setMyEnvironment():
    SceneSettings.set_clip_end(20000)
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value[0] = 1
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value[1] = 1
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value[2] = 1
    SceneSettings.set_shading()
    
# -----------------------------------------------------------------------------
    
def get_mesh_obj_named(obname):
    for o in bpy.context.scene.objects:
        if o.type == 'MESH' and o.name == obname:
            return o
    return None

# -----------------------------------------------------------------------------

    
# Join the two meshes together and name the resulting mesh name
def meshes_join(name, me1, me2):
    bm = bmesh.new()
    bm.from_mesh(me1)
    #print(bm)
    bm.from_mesh(me2)
    #print(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me

# -----------------------------------------------------------------------------    

# Join the mesh in the object ob_new to the existing mesh object eith name obname
def mesh_obj_join_existing(obname, ob_new):
    
    ob_orig = None
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            if o.name == obname:
                ob_orig = o
                
    if ob_orig != None:
        #print('Found orig', ob_orig)
        
        me_orig = ob_orig.data
        me_joined = meshes_join(obname, me_orig, ob_new.data)
        
        ob_orig.data = me_joined
        bpy.data.meshes.remove(me_orig, do_unlink=True)
        return ob_orig
    else:
        return None
    #    me_new = ob_new.data
    #    me_new.name = obname
    #    ob_new.name = obname
    #    return ob_new   
    
# -----------------------------------------------------------------------------

def lock_obj_to_parent(obj):
    if obj.parent != None:
        #print(obj.name)
        obj.lock_location[0] = True
        obj.lock_location[1] = True
        obj.lock_location[2] = True
        obj.lock_rotation[0] = True
        obj.lock_rotation[1] = True
        obj.lock_rotation[2] = True
        obj.lock_scale[0] = True
        obj.lock_scale[1] = True
        obj.lock_scale[2] = True

# -----------------------------------------------------------------------------

