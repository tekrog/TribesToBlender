# TribesToBlender
Import Starsiege: Tribes models into Blender 3.0+
Currently, only .DTS files are supported for import, these are the static and animated meshes used by Tribes.

# Installation
In GitHub go to Code > Download as .zip
In Blender > Edit > Preferences > Add-ons > Install > browse to .zip
Then enable the add-on by checking the box next to "Import-Export: Import-DTS"

Once installed, go to File > Import and DarkStar (.dts) is now an option.

# Supported Features
The following model features are supported:
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

# Known Issues
Below are the currently known issues:
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
* Add support for DIS, TED, and DIL files.
