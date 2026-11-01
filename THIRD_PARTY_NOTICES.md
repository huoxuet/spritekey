# Separately installed dependencies and external tools

SpriteKey's newly written Python, documentation, tests and original geometry demo
are offered under the accompanying MIT license. That license does not replace
the licenses of separately obtained software or user-supplied media.

This source tree / pure Python wheel does **not** distribute dependency source,
dependency binaries, models, FFmpeg binaries or game pictures.

| Dependency | Own license / source |
|---|---|
| NumPy | BSD-3-Clause for NumPy itself; wheels can include additional separately licensed libraries. https://numpy.org/doc/stable/license.html |
| Pillow | MIT-CMU; dependency builds can contain separately licensed codec libraries. https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| OpenCV library (4.5.0 and later) | Apache-2.0 for the OpenCV library; bundled components can have additional licenses. https://opencv.org/license/ |
| opencv-python-headless Python packaging code | MIT, copyright Olli-Pekka Heinisuo; distinct from the OpenCV library license. https://github.com/opencv/opencv-python/blob/master/LICENSE.txt |
| Python | PSF license and its own included notices. https://docs.python.org/3/license.html |
| FFmpeg 7 (external program only) | Build-dependent LGPL/GPL and component licenses. Obtain the executable and its notices from its distributor. https://ffmpeg.org/legal.html |
| setuptools (build only) | MIT; separately installed build backend. https://github.com/pypa/setuptools/blob/main/LICENSE |

An installed NumPy wheel inspected for this work reports additional bundled
library licenses, including OpenBLAS and compiler runtime notices. The installed
OpenCV headless 4.13.0.92 wheel's distribution metadata reports `License: Apache
2.0`, while both installed `cv2/LICENSE.txt` and
`opencv_python_headless-4.13.0.92.dist-info/LICENSE.txt` contain the MIT license,
copyright Olli-Pekka Heinisuo, for the Python packaging code. The metadata field
does not override those accompanying license files. Check metadata, the actual
included license files and component notices separately. These observations
describe the tested environment; they do not mean all future wheel builds have
identical contents. Preserve dependency distributors' complete accompanying
notices when redistributing those dependencies. SpriteKey's MIT grant covers only
SpriteKey.

Tested dependency metadata: Python 3.12.14, NumPy 2.3.5, Pillow 12.3.0,
opencv-python-headless 4.13.0.92 (runtime cv2 reports 4.13.0). Runtime manifest
records the actual versions for each processing run.

The fresh public-package installation additionally tested NumPy 2.5.4, Pillow
13.0.0 and opencv-python-headless 5.0.0.93. The latter still reports Apache 2.0
in distribution metadata and MIT in both cv2/LICENSE.txt and its dist-info
LICENSE.txt for the Python packaging, matching the distinction above. NumPy
metadata reports BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0; preserve
its complete included notices rather than interpreting the table as a full
wheel-component license inventory.
