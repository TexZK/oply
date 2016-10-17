Summary
=======

`oply` is a Python library to emulate the Yamaha OPL FM synthesizers.

The core itself is based on the mighty *Nuked OPL3* emulation library by
Alexey Khokholov, ported to Python in a more object-oriented fashion,
following the *PEP 8* coding style.

It is currently written in pure Python; developed for 3.5, but it might be
backwards-compatible down to the glorious 2.7.  This allows maximum
portability.

Beware that its timing performance are awful, taking a **very** long time
to render even a few seconds of sound.  I have not tried with *PyPy* or any
other accelerators yet.  Maybe in the future there will be wrappers to
high performance libraries (say, written in C), with the pure Python
implementation as a mere fallback.

Said that, this library was written more out of my own curiosity, and because
I was lacking a way to render the *IMF* chunks of *Wolfenstein 3D* in my
`pywolf` project, instead of relying on external binaries, although it takes
hours to export all of its assets... whatever! xD

-------------------------------------------------------------------------------

License
=======

> oply - Yamaha OPL emulation with Python
> Copyright (C) 2016 Andrea Zoppi
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
>
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License
> along with this program.  If not, see <http://www.gnu.org/licenses/>.
