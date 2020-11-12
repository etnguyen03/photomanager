# photomanager

_Because fuck Google Photos._

**NOTE**: Definitely not ready for any production usage.
My goal is to be somewhat close to production ready by the time that
Google Photos goes non-free (currently set for July 2021) but
that might be missed.

`photomanager` is an effort to clone as many features of Google Photos as possible
in a high-quality manner while still remaining free, open-source software accessible to all. 

The goals include:

* Per-user authentication
* Nextcloud integration, perhaps with a simple read-only mount
  * Easier to auto-upload - app already exists
* [Tensorflow NASNet](https://www.tensorflow.org/api_docs/python/tf/keras/applications/NASNetMobile)
for autotagging images
* [`facenet-pytorch`](https://github.com/timesler/facenet-pytorch) for face recognition

---

This project is definitely not endorsed by Google, Alphabet Inc., or anyone else affiliated
with Google Photos.

Copyright (c) 2020 Ethan Nguyen and contributors. All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.