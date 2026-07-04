# TribesToBlender
Import Starsiege: Tribes models into Blender 3.0+

Currently, .DTS and .DIS files are supported for import, these are the static and animated meshes and BSP meshes used by Tribes.

.DIS model support added courtesy of [Jobo's DIS to OBJ converter](https://github.com/jcmolnar/Tribes-DIS-to-OBJ).

# Installation
In GitHub go to Code > Download as .zip

In Blender > Edit > Preferences > Add-ons > Install > browse to .zip

Then enable the add-on by checking the box next to "Import-Export: Import-Starsiege-Tribes"

This add-on was tested on Blender 3.2 and 5.1.

# Usage
Once installed, go to File > Import and Darkstar Shapes(.dis, .dts) is now an option.

All shapes and textures need to be extracted from their .vol (Tribes 1.11) or .zip (Tribes 1.40). The importer will pick up the textures automatically if they are in the same folder. .DIS shapes require their .DIS, .DIG, .DML, and textures to be extracted. .DTS shapes require their .DTS and textures to be extracted.

# Supported Features
The following .DTS model features are supported:
* Animations
* Static meshes
* Collision meshes
* Debris meshes
* Hulk meshes
* Levels of Detail (LODs)(Each level will have a number after the name of the root mesh)
* Textures
  * If the texture files are in the same directory as the .dts file, they will be automatically imported and applied to the model
* IFL sequences (animated materials)
  * This does not include animated UVs (this is how the Plasma Gun animates the cartridge when fired)
* Armors with bones
  * Some of the animations slide, this is most likely a keyframing issue
* Vehicles
  
The following .DIS model features are supported:
* BSP meshes
* Levels of Detail (Each level will have a number after the name of the root mesh. 00 has the most detail)
* Option on Import window to flip the U or V direction of the textures, usually not needed.

# Known Issues
Below are the currently known .DTS issues:
* Sub-animations do not work (flames on the vehicles)
* Some of the armor animations slide, an additional keyframe most likely needs to be inserted before transitioning between animations
* Not all of the vertex animations work properly (Sensor Jammer)
* Animated UVs are not supported.
* Importing multiple models at the same can break the hierarchy and overlap the timeline markers.
  * Don't import more than one model at a time into a scene.

# Wishlist
Items we would like to add to the add-on.
* Animated meshes / vertex animations (like the Camera and deployable sensor)
  * There is an "animated-scaling" branch that is adding support for this, but there is an issue with the animation origin.
* Change animation markers to use actions instead.
* Auto-create bones and move animations to bones.
* Add support for animated UVs.
* Add support for TED, and DIL files.
