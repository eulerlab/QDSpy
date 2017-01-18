### QDSpy v.72 beta

This is a software for generating and presenting stimuli for visual neuroscience. It is written in Python and based on  (http://wvad.mpimf-heidelberg.mpg.de/abteilungen/biomedizinischeOptik/software/qds/), uses OpenGL and primarly targets Windows 7 (and above).

*Note, this is an early beta version.*

####Documentation

For documentation, see http://qdspy.eulerlab.de.

####Release notes

v0.73beta (January 2017)

* Installation instructions extended (2016-12-20 and 2017-01-18).
* Dependencies changed from Qt4 to Qt5. The background is that many packages, 
  including Anaconda (from version 4.2.0), are now moving to Qt5 for several 
  reasons. QDSpy is now using Qt5 and is now compatible to the latest version
  of the Anaconda distribution
* Bux fix: The GUI is now scaled if an HD display is detected - before it was
  not usable on small HD screens. The mechanism is fairly simple: if one of the
  connected screens has a pixel density larger than 110 dpi (currently defined
  in `QDSpy_dpiThresholdForHD` in ``QDSpy_global.py``) then all GUI elements are
  scaled by this pixel density devided by 100. The font size of the text in the
  history is treated differently; dependent on whether an "HD" display was 
  detected one of two pre-defined font sizes are used 
  (see `QDSpy_fontPntSizeHistoryHD` and `QDSpy_fontPntSizeHistoryHD` in 
  ``QDSpy_global.py``).
           

v0.72 beta (August 2016) 

* Bug fix: GUI for adjusting LED currents now remains active after sending a 
  change to the lighcrafter. "Refresh display info" button now works and LED
  status is updated after the automatic execution of ``__autorun.pickle``.


v0.71 beta (July 2016) 

* **Videos (AVI containers) now work** except for the rotation parameter, which uses
  a corner instead of the centre. The commands are `DefObj_Video()`, `Start_Video()` 
  and `GetVideoParamters()`. Note that the latter now returns a dictionary instead
  of a list.
* Like `GetVideoParamters()`, `GetMovieParamters()` now also returns a dictionary.
* The GUI has been reorganized:

  * A font is used that works on all Window versions (7 and higher).
  * *Lightcrafter only*: The `LEDs: enable` button allows switching off the LEDs
    and changes to manual LED control (for details, see section :doc:`lightcrafter`).
  * A new tab called "tools" was added; currently in contains a very simple 
    interface to a USB camera (e.g. for observing the stimulus).
  * A "Wait for trigger: ..." button has been added; *this is not yet functional*.
  * Duration of stimulus is shown.
  * Minor fixes.


v0.70 beta (July 2016) 

* Now reports GLSL version
* Fixed error when QDSpy GUI does not find a compiled `__autorun`.
* Stimulus folder can now be selected using the  `Change folder` button. Note
  that at program start, QDSpy always pre-selects the default stimulus folder
  defined in the `QDSpy.ini` file
* Cleaning up some pyglet-related code
* Fixed that `psutil` was required even with `bool_incr_process_prior=False`
* Added two entries to the `[Display]` section of the configuration file: 
  `bool_markershowonscreen` determines if the marker ("trigger") that is send
  via an I/O card is indicated as a small box in the right-bottom corner of
  the screen. Entry `int_markerrgba` (e.g. = 255,127,127,255) defines the 
  marker color as RGB+alpha values.
* Starting the GUI version does not require a command line parameter anymore
* Added a new optional command line parameter ``--gui``, which when present
  directs all messages (except for messages generated when scripts are 
  compiled) to the history window of the GUI. 
* If the `QDSpy.ini` file is missing, it will be recreated from default values.
  From now on, the `QDSpy.ini` file will not be any longer in this repository to 
  prevent that new versions overwrite setup-specific settings (e.g. hardware 
  use, digital I/O configuration, etc.)
* Removed currently unused tab "Setting" in GUI
* Changed code for increasing process priority via `psutil` 
* Added pre-compiled ``hidapi`` packages for Python 3.5.x (``hid.cp35-win_amd64.pyd``); 
  the version for Python 3.4.x was renamed to ``hid.cp34-win_amd64.pyd``. 
* **Now QDSpy fully supports Python 3.5.x.** The installation instructions were 
  updated accordingly.
* Fixed bug in drawing routines for sectors and arcs
* 'Q' now aborts stimulus presentation for both the command line and GUI 
  version of QDSpy
* Refractoring of the code that interfaces with the graphics API (currently
  OpenGL via pyglet)
* Fixed a bug in the way the scene is centered and scaled.
* Added a **stimulus control window** to be displayed on the GUI screen when 
  stimulus presentation is running fullscreen on a different display. This is beta;
  the performance of drawing stimuli on different screens in parallel needs to
  be carefully tested on different machines.
  Added two entries to the `[Display]` section of the configuration file: 
  `bool_use_control_window` activates or deactivates the control window, and 
  `float_control_window_scale` is a scaling factor that defines the size of the
  control window.
* When upgrading a QDSpy installation, new configuration file parameters are now
  automatically added. 
  **Important:** for consistency, the names of some entries in the configuration 
  file needed to be changed: `str_digitalio_port_out`, `str_digitalio_port_in`,
  `str_led_filter_peak_wavelengths`, `str_led_names`, `str_led_qtcolor`, and 
  `str_markerrgba`. **This needs to be corrected manually in any pre-existing
  configuration file in an existing installation.** Alternatively, the configuration
  file can be deleted, triggering QDSpy to generated a new one with default values.  
* Fixed a bug that caused QDSpy to freeze when changing stage parameters and
  then playing a stimulus.  
* End program cleanly and with a clear error message when digital I/O is enabled
  in the configuration file but the Universal Library drivers are not installed. 
  The default for the configuration file is now `bool_use_digitalio = False`.


v0.6 beta (April 2016) 

* Bug fixes
* Added `DefObj_Video()`, `Start_Video()` and `GetVideoParamters()` commands. 
  Not yet fully implemented and tested; do not use yet.
* Added `GetMovieParameters()` command
* Fixed `GetDefaultRefreshRate()` command; now reports requested frame rate.
* Added `[Tweaking]` section to configuration file. Here, parameters that tune
  the behaviour of QDSpy are collected. The first parameter is `bool_use3DTextures`;
  it determines, which of pyglets texture implementations is used to load and
  manage montage images for movie objects (0=texture grid, 1=3D texture).
* Added instructions to the documentation of `DefObj_Movie()` how to convert
  a movie image montage used for the previous QDS with QDSpy. Key is that - in 
  contrast to QDS - QDSpy considers the bottom-left frame of a montage the first
  frame of the sequence.


v0.5 beta (December 2015) 

* Bug fixes
* Documentation updated
* Gamma correction of display now possible (see section 
  :doc:`how_QDSpy_works`)
* Now catches errors generated when compiling shader scripts.
* Changed stage parameters (magification, center, rotation, etc.) are now 
  written to the configuration file.
* Writes the log automatically to a file. The log contains machine-readable 
  tags for the data analysis.


v0.4 alpha (November 2015) 

* Migrated to Python 3.4.3
* Added GUI
* Bug fixes
* Added rudimentary support for controlling a lightcrafter device 
* Added movie commands, currently only copying what the old QDS commands did.
* Added a shader that acknowledges colour and alpha value of its object 
  ("SINE_WAVE_GRATING_MIX").


v0.3 alpha (March 2015) 

* Minor bug fixes
* Fixed transparency of objects (works now)

v0.2 alpha (before 2015)

* Basic functionality, proof of concept

