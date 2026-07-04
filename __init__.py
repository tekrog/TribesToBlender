# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#################################################

# -------------------
# Tribes to Blender
# -------------------
# Add-on: import-Starsiege-Tribes
# Author: Noxwizard and Krogoth
# Description: Imports Starsiege: Tribes files into Blender 3.0+.
#              Original python DIS to OBJ script created by Jobo.

#################################################

bl_info = {
    "name" : "Import-Starsiege-Tribes",
    "author" : "Noxwizard and Krogoth",
    "description" : "Imports Starsiege: Tribes DTS and DIS files.",
    "blender" : (3, 0, 0),
    "version" : (0, 0, 1),
    "location" : "File > Import-Export",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "Import-Export"
}

import bpy
import os
from .DTSImporter import load_dts
from .DISImporter import load_dis

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, FloatProperty, BoolProperty

class DarkstarImporter(bpy.types.Operator, ImportHelper):
    bl_idname = "dynamix.dts"
    bl_label = "Import Starsiege: Tribes shapes"
    bl_description = "Imports Starsiege: Tribes shapes"

    filter_glob: StringProperty(
        default="*.dis;*.dts;",
        options={'HIDDEN'}
    )
    
    # Option to flip the V texture on .DIS import
    flip_v: BoolProperty(
        name="Flip V",
        description="Flip the V texture coordinate if textures appear upside down",
        default=False
    )
    # Option to flip the U texture on .DIS import
    legacy_uv: BoolProperty(
        name="Legacy UV (Flip U)",
        description="Flip the U texture coordinate if textures appear mirrored",
        default=False
    )
    
    # Called after file selection
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # Blender calls check() when a file has been chosen
    def check(self, context):
        return True

    # Called after file selection
    def execute(self, context):
        extension = os.path.splitext(self.filepath)[1].lower()

        if extension == '.dis':
            load_dis(
                self.filepath,
                context,
                flip_v=self.flip_v,
                legacy_uv=self.legacy_uv
            )

        elif extension == '.dts':
            load_dts(self.filepath, context)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        if self.filepath.lower().endswith(".dis"):
            layout.label(text="UV Options")
            layout.prop(self, "flip_v")
            layout.prop(self, "legacy_uv")

def menu_func_import(self, context):
    self.layout.operator(DarkstarImporter.bl_idname, text="Darkstar Shapes (.dis, .dts)")

def register():
    bpy.utils.register_class(DarkstarImporter)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(DarkstarImporter)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)