### QDSpy

This is a Python software for scripting and presenting stimuli for visual neuroscience. 
It is based on QDS (http://wvad.mpimf-heidelberg.mpg.de/abteilungen/biomedizinischeOptik/software/qds/), 
uses OpenGL and primarly targets Windows but, with a few changes, may also run on other operating systems.

*Note, this is an early, experimental (alpha) version.*

See documentation in ``/QDSpy/html/index.html``.

To get started, see ``/QDSpy/html/installation.html``.

####Known issues

* Videos won't stop correctly; do not use yet.
  Minor: While partial transparency and scaling works with videos, rotation
  does not yet (wrong rotation axis?)

* Shader-enabled objects may not be drawn in the correct order, which means
  that shader objects can flicker when they overlap.

* Starting a movie for the first time in a script can cause a delay of ~200 ms.
  A work-around is to start the movie right at the beginning of the script
  starting section, for example:
  ::
    ...
    QDS.StartScript()
    QDS.Start_Movie(1, (0,0), [ 0,  0, 1,  1], (1,1), 0, 0)
    QDS.Scene_Clear(2.00, 0)
    ...

  This avoids the delay later during the time-critical parts of a stimulus. 

####To do

* URGENT: Fix video presentation
* URGENT: Recompile hidapi for Python 3.5. Implement use of correct pre-compiled
  hidapi module depending on Python version (3.4 vs. 3.5)
* Check x-y scaling
* Check timing of digital I/O signals (i.e. triggers).
* Complete lightcrafter interface.
* For color modes >1 (special lightcrafter modes), movie images need to be
  converted with the respective cvolor scheme.
* Add stimulus control window to be displayed on the GUI screen when stimulus
  presentation is running fullscreen on a different display.
* Add possibitity to control timing (i.e. sync refresh to an external source) 
  on genlock-enabled NVIDIA and/or ATI graphic cards.

####Release notes

* Now reports GLSL version
* Fixed error when QDSpy GUI does not find a compiled `__autorun`.
* Stimulus folder can now be selected using the  `Change folder` button. Note
  that at program start, QDSpy always pre-selects the default stimulus folder
  defined in the `QDSpy:ini` file
* ...

v0.6 beta (April 2016)
* Bug fixes
* Added ``DefObj_Video()``, ``Start_Video()`` and ``GetVideoParamters()`` commands. Not yet fully implemented and tested; do not use yet.
* Added ``GetMovieParameters()`` command
* Fixed ``GetDefaultRefreshRate()`` command; now reports requested frame rate.
* Added ``[Tweaking]`` section to configuration file. Here, parameters that tune the behaviour of QDSpy are collected. The first parameter is ``bool_use3DTextures``; it determines, which of pyglets texture implementations is used to load and manage montage images for movie objects (0=texture grid, 1=3D texture).
* Added instructions to the documentation of ``DefObj_Movie()`` how to convert a movie image montage used for the previous QDS with QDSpy. Key is that - in contrast to QDS - QDSpy considers the bottom-left frame of a montage the first frame of the sequence.

v0.5 beta (December 2015)
* Bug fixes
* Documentation updated
* Gamma correction of display now possible (see section How QDSpy works)
* Now catches errors generated when compiling shader scripts.
* Changed stage parameters (magification, center, rotation, etc.) are now written to the configuration file.
* Writes the log automatically to a file. The log contains machine-readable tags for the data analysis.

v0.4 alpha (November 2015)
* Migrated to Python 3.4.3
* Added GUI
* Bug fixes
* Added rudimentary support for controlling a lightcrafter device
* Added movie commands, currently only copying what the old QDS commands did.
* Added a shader that acknowledges colour and alpha value of its object (``SINE_WAVE_GRATING_MIX``).

v0.3 alpha (March 2015)
* Minor bug fixes
* Fixed transparency of objects (works now)

v0.2 alpha (before 2015)
* Basic functionality, proof of concept
