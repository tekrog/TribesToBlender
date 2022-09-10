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
# Blender for Science
# -------------------
# Add-on: import-Starsiege-Tribes
# Author: Noxwizard and Krogoth
# Description: Imports Starsiege: Tribes files into Blender 3.0+.

#################################################

bl_info = {
    "name" : "Import-DTS",
    "author" : "Noxwizard and Krogoth",
    "description" : "Imports Starsiege: Tribes DTS files.",
    "blender" : (3, 0, 0),
    "version" : (0, 0, 1),
    "location" : "File > Import-Export",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "Import-Export"
}

import bpy
from .main import ImportDTS

def menu_func_import(self, context):
    self.layout.operator(ImportDTS.bl_idname, text="DarkStar (.dts)")

def register():
    bpy.utils.register_class(ImportDTS)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportDTS)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)