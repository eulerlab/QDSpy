
## QDSpy v.77 beta

This is a software for generating and presenting stimuli for visual neuroscience. It is based on QDS, developped in the former Dept. of Biomedical Optics at the MPI for Medical Research in Heidelberg. QDSpy is written in Python, uses OpenGL and primarly targets Windows 7 and above.

*Note, this is still a beta version.*
*For disclaimer, see [here](http://qdspy.eulerlab.de/disclaimer.html#disclaimer-of-warranty).*

### Documentation

For documentation, see [here](http://qdspy.eulerlab.de).  
To jump to installation, see [here](http://qdspy.eulerlab.de/installation.html#installation).

### Release notes

#### v0.77beta

* Bug fix: In Python 3.7, terminating QDSpy caused a `RuntimeError: dictionary changed size during iteration`; fixed.
* Bug fix: Default values for Arduino user-defined buttons fixed.
* Bug fix: Issue with loading gamma LUTs via `windll.gdi32.SetDeviceGammaRamp` fixed.
* New digital I/O feature added: In addition to the marker pin, two user output pins can be now be defined in 
  the ``QDSpy.ini`` file. These allow to control simple external TTL-compatible hardware from the GUI, which 
  now contains two user buttons to switch the signals at the user pins. A simple example application is controlling 
  a drug puffing system. Note that this feature is not yet implemented for the Arduino as I/O device.
  See [`inifile`](http://qdspy.eulerlab.de/inifile.html) for details on the new parameters.
* Changes by [Tom Boissonnet](https://github.com/Tom-TBT):
    * Bug fix in probing center feature.
    * Parameters added to ``QDSpy.ini`` file: ``float_gui_time_out`` (in seconds), which deals with potential problems 
      when loading very large stimuli; ``str_antimarkerrgba``, defining the colour of the "anti" marker, which "blanks" 
      the marker area on the screen when the marker is not displayed. This prevents large stimuli from interacting with 
      the marker display.
* **IMPORTANT**: The ``QDSpy.ini`` file contains new parameters, which need to be added to the existing ``QDSpy.ini`` file,
  otherwise QDSpy will crash. The easiest way to do so, is to rename the file to, for example, ``QDSpy.ini_COPY``. Then start
  QDSpy and let it generate a fresh configuration file. Open both the new file and your copy in parallel and change the
  parameters in the new file according to your previous settings. See see :doc:`inifile` for further details on the new
  parameters.
* Small bug fix in the GUI.

#### v0.76beta - experimental branch

* 2017-08-13: Accelerated program start (i.e. on PCs with many cores) by simplifying communication between stimulation process
  and GUI, avoiding time-consuming sync manager and by communicating with integers instead of strings.
* 2017-08-11: Bug fix: Probing center feature ([Tom Boissonnet](https://github.com/Tom-TBT))
* Experimental support for an Arduino as low-cost digital I/O device (timing not yet thoroughly tested!).
* New feature contributed by [Tom Boissonnet](https://github.com/Tom-TBT) (Asari lab, EMBL Monterotondo):     
  It is found on the GUI tab "Tools". When pressing "Start probing center",
  a spot appears on the stimulus screen.
  The spot can be moved (dragged) with the left mouse button pressed.
  Changing the spot parameters in the GUI changes the spot immediately.
  The tool can, for example, be used to roughly explore the receptive field of
  a retinal ganglion cell. The probing mode can be left
  by either pressing the right mouse button (saving the position to the log),
  or by pressing "Abort" in the GUI.    
* **IMPORTANT**: The ``QDSpy.ini`` file contains (a) new parameter(s), which need to be added to the existing 
  ``QDSpy.ini`` file, otherwise QDSpy will crash. The easiest way to do so, is to rename the file to, for example,
  ``QDSpy.ini_COPY``. Then start QDSpy and let it generate a fresh configuration file. Open both the new file and 
  your copy in parallel and change the parameters in the new file according to your previous settings. See see 
  :doc:`inifile` for further details on the new parameters.

#### v0.75beta (April 2017)

* Bug fix: Problems with "ghost images" when playing more than one movie or video were fixed. Now movie/video objects that are restarted before the previous run was finished are first automatically stopped and ended. Also, movies/videos were also forwarded for no-duration scenes (e.g. a change in object colour), which led to changes in the movie/video frame rate. This should now be fixed as well.
* Bug fix: The first command in a loop was ignored; this is fixed now.
* Bug fix: ``__autofile.py`` handling was restructured: When no ``__autorun.py``
  file exists in the ``.\Stimuli`` folder, QDSpy warns and runs a default instead. An ``__autorun.py`` does no
  longer have to be present in ``.\Stimuli``.
* **New feature**: Using the "screen overlay mode", stimuli with up to 6 different
  wavelengths (hexachromatic) can be shown by extending the presentation area to
  two neighbouring display devices (i.e. two lightcrafters with different sets of
  LEDs). See [`inifile`](http://qdspy.eulerlab.de/inifile.html) for details on the new configuration parameters in
  section ``[Overlay]`` and
  [Screen overlay mode](http://qdspy.eulerlab.de/how_QDSpy_works.html#screen-overlay-mode) for instructions.
  This feature was inspired by the paper _"A tetrachromatic display for the
  spatiotemporal control of rod and cone stimulation"_ by Florian S. Bayer and
  colleagues (Bayer et al., 2015, J Vis [doi:10.1167/15.11.15](https://www.ncbi.nlm.nih.gov/pubmed/26305863)).
* **IMPORTANT**: The ``QDSpy.ini`` file contains a couple of new parameters,
  including a new section called ``[Overlay]``. Thus, the new parameters need to
  be added to the existing ``QDSpy.ini`` file, otherwise QDSpy will crash.
  The easiest way to do so, is to rename the file to, for example,
  ``QDSpy.ini_COPY``. Then start QDSpy and let it generate a fresh configuration
  file. Open both the new file and your copy in parallel and change the parameters
  in the new file according to your previous settings. See see :doc:`inifile`
  for further details on the new parameters.
* **Known issues**:
  * The GUI controls for the "screen overlay mode" are already present but not
    yet working. A work-around is changing the settings directly in ``QDSpy.ini``.
  * Objects that use shaders are not yet correctly displayed in "screen overlay
    mode".
  * ``SetColorLUTEntry()`` does not yet handle a LUT with more than 3 colours.
  * When starting QDSpy the stimulus screen may sometimes go white; as soon as
    the first stimulus is presented, the screen behaves normal.

#### v0.74beta (March 2017)

* Added `hid.cp36-win_amd64.pyd` to ``.\Devices`` to enable ``hid`` under Python
  3.6 (comes with Anaconda version 4.3.x). This means that now QDSpy should
  be compatible with the newest Anaconda distribution.
* Attempted to simplify path management: ``__autorun.pickle`` is not anymore
  required in the stimulus folder
* LED pre-settings for lightcrafter was extended: now for each LED also
  the default current, the maximal current, the index of the lightcrafter
  device (0 or 1), and the LED index (which LED position within the
  lightcrafter) are defined in ``QDSpy.ini``.
* Up to two lightcrafters can be handled; the GUI has been changed accordingly.
* **IMPORTANT**: Note that the ``.pickle`` format has changed and therefore all stimuli need to
  be recompiled. To avoid confusion, delete all ``.pickle`` files in the
  ``\QDSpy\Stimulus`` folder.
* **IMPORTANT**: The ``QDSpy.ini`` file contains a couple of new parameters,
  including a new section called ``[Overlay]`` (the latter is work in progress
  and concerns a feature that is not yet fully implemented yet. Please ignore
  for now).
  Thus, the new parameters need to be added to the existing ``QDSpy.ini`` file,
  otherwise QDSpy will crash. The easiest way to do so, is to rename the file
  to, for example, ``QDSpy.ini_COPY``. Then start QDSpy and let it generate
  a fresh configuration file. Open both the new file and your copy in parallel
  and change the parameters in the new file according to your previous
  settings. See see :doc:`inifile` for further details on the new parameters.
* Documentation was updated and extended (including, for example, a detailed
  explanation of the parameters in ``QDSpy.ini``).

#### v0.73beta (January - February 2017)

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
* Bug fix: Stimulus duration now calculated correctly.
* Bug fix: `GetStimulusPath()` now returns also to correct path for stimulus
  files in a subfolder of the default stimulus folder.


#### v0.72 beta (August 2016)

* Bug fix: GUI for adjusting LED currents now remains active after sending a
  change to the lighcrafter. "Refresh display info" button now works and LED
  status is updated after the automatic execution of ``__autorun.pickle``.

#### v0.71 beta (July 2016)

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

#### v0.70 beta (July 2016)

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


#### v0.6 beta (April 2016)

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


#### v0.5 beta (December 2015)

* Bug fixes
* Documentation updated
* Gamma correction of display now possible (see section
  :doc:`how_QDSpy_works`)
* Now catches errors generated when compiling shader scripts.
* Changed stage parameters (magification, center, rotation, etc.) are now
  written to the configuration file.
* Writes the log automatically to a file. The log contains machine-readable
  tags for the data analysis.


#### v0.4 alpha (November 2015)

* Migrated to Python 3.4.3
* Added GUI
* Bug fixes
* Added rudimentary support for controlling a lightcrafter device
* Added movie commands, currently only copying what the old QDS commands did.
* Added a shader that acknowledges colour and alpha value of its object
  ("SINE_WAVE_GRATING_MIX").


#### v0.3 alpha (March 2015)

* Minor bug fixes
* Fixed transparency of objects (works now)

#### v0.2 alpha (before 2015)

* Basic functionality, proof of concept
