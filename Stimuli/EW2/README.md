# Stimulus description
In Eyewire2 stimuli were chirp, moving bar (MB) and mouse camera movies (MCs).

The original QDSpy stimulator scripts for [chirp](./Chirp.py), [MB](./DS.py) and [MCs](MouseCam_Right.py) are included in this folder.  
For completeness, also the left-retina version was included [MouseCam_Left.py](), which was not used in Eyewire2.

## Chirp
The chirp had a spot with a diameter of 1000 µm and otherwise follows previous publications.

## Moving bar 
The moving bar directions in the script were (0, 180, 45, 225, 90, 270, 135, 315) degrees.  
In the setup chamber this resulted in the following directions of the moving bar (↓, ↑, ↙, ↗, ←, →, ↖, ↘), where e.g. "↓" means back to front.
The bar width (the dimension that is orthogonal to the direction of motion) was 300 µm, the speed 1000 µm/s, and the length 1000 µm.

## Retina orientation
The retina was from the right eye. Ventral was in the back of the setup chamber.  
So this is the orientation of the retina in the setup chamber:
```
----- Ventral ----
Nasal ---- Temporal
----- Dorsal -----
```
For the MB, 0° therefore means ventral to dorsal motion.
90° means temporal to nasal motion.

## Mouse camera movies
MCs were similar as in [Höfling et al. 2024](https://elifesciences.org/articles/86860) which were derived from recordings by [Qiu et al. 2021](https://www.cell.com/current-biology/fulltext/S0960-9822(21)00676-X).
There are different MC stimuli, e.g. MC-16 and MC-20, that are all based on the same 113 five-second movie clips.  
Each MC stimulus MC-X is described by a sequence [test/train1-X/test/train2-X/test](https://iiif.elifesciences.org/lax:86860%2Felife-86860-fig1-v1.tif/full/1500,/0/default.jpg),
where:
- the test sequence, consisting of five movie clips, is the same for all MC versions and is shown three times (the beginning, the middle and the end),
- and the train sequences train1-X and train2-X consist of 54 movie clips, each, that are differently ordered for each MC stimuli MC-X.

Each MC therefore consists of a sequence of 123 five-second movie clips, with 123 corresponding triggertimes.
The order of the train sequences is stored in [RandomSequences.txt]().
With [mc_to_numpy.py]() you can generate numpy arrays that correspond to the MC stimuli.
With [mc_arrays/load_mc_array.ipynb]() you can display them as they would appear in QDSpy.
In the setup chamber the movies were rotated by 90 degrees counter-clockwise.
