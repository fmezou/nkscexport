:github_url:

.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

**********
DarkBridge
**********

Converts Nikon sidecar files into Darktable sidecars.

Synopsis
--------

usage: :samp:`darkbridge [-h] [-l LOG_LEVEL] [-v] {convert,list,search} ...`

usage: :samp:`darkbridge list [-h] [-a] [-d] [-r] [filename ...]`

usage: :samp:`darkbridge convert [-h] [-f] [-n] [-r] [filename ...]`

usage: :samp:`darkbridge search [-h] (-p PROCESSING | -m META) [-c] [-r]
[filename ...]`

Description
-----------

:program:`darkbridge` is a utility that converts Nikon NX Studio :file:`.nksc`
sidecar files into sidecar files compatible with Darktable. It helps
photographers migrate adjustment data from Nikon’s workflow to Darktable
without manually recreating edits.

Darkbridge ignores files that not matching following criteria:

* a Nikon sidecar file is in a :file:`NKSC_PARAM` folder
* a Nikon sidecar is named :file:`{basename}.{extension}.nksc` where
  :file:`{basename}.{extension}` is the image file name
* a darktable sidecar exists with the same name that the Nikon sidecar
  in the parent folder.

The script only supports image files supported by NX Studio [1]_ :
:file:`.nef`, :file:`.nrw`, :file:`.jpg`, :file:`.jpeg`, :file:`.tif`,
:file:`.tiff`, :file:`.hif`, :file:`.nefx`, :file:`.mpo`.

The options are as follows:

.. program:: darkbridge

.. option:: convert

    Converts Nikon sidecar files into Darktable sidecar files.

.. option:: list

    List metadata from Nikon sidecar files. Existance of darktable
    sidecar file is ignored when this option is used.

.. option:: search

    Search an image adjustment (processing) or a metadata into Nikon
    sidecar files.

.. option:: -h, --help

    Show this help message and exit

.. option:: -l, --log-level LOG_LEVEL

    Logging messages which are less severe than level will be ignored.
    Level may be set to: 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
    'CRITICAL'. Upper case or lower case are accepted and level is set
    to 'NOSET' by default. Log entries are write in a file in the
    current directory. If this option is not present or set to NOSET, no
    logfile is created

.. option::  -v, --verbose

    Increase the verbosity of report. By default, the report is
    a summary with image name and a set of indicators. A single
    ``-v`` lists relevant metadata (i.e. non-empty) and active image
    adjustments. A second ``-v`` (or ``-vv``) list metadata's content
    and image adjustment parameters. A third ``-v`` or ``-vvv``) list
    all metadata and image's adjustment whatever its status.

.. option:: -V, --version

    Show program's version number and exit

.. option:: -f, --force

    Overwrite existing sidecar files without prompting for confirmation.

.. option:: -n, --dry-run

    Run in preview mode without any sidecar writing.


.. option:: -p, --processing PROCESSING

    Name of the image adjustment (processing) to search. The search
    return the processing's name where substring 'PROCESSING' is found
    and if it is an active processing. The search is case-sensitive.

.. option:: -m, --meta META

    Name of the metadata's field to search. The search return the name
    of the field where substring 'META' is found. The search focuses on
    the field name and not the content of the field. The search is
    case-sensitive.

.. option:: -r, --recursive

    Make a recursive search of images files in subfolders.

.. option:: filename

    Files or directories to parse. For each item that name a supported
    image file, darkbridge parses the associated Nikon sidecar file and
    copy metadata in the darktable sidecar file. For each item that name
    a directory, darkbridge list supported images files contained in the
    directory, and parses each files. If no file are given, the content
    of the current directory is used.

.. [1] Nikon, NX Studio Supported Formats,
    https://nikonimglib.com/nxstdo/onlinehelp/en/supported_formats_4.html

Exit status
-----------

==  ====================================================================
0   No error
1   An error occurred (error messages are print on stderr stream
    console).
2   Invalid argument. An argument of the command line isn't valid
    (see Usage).
==  ====================================================================

Example
-------
Convert the sidecar file :file:`./NKSC_PARAM/landscape.NEF.nkcs` into
:file:`./landscape.NEF.xmp`::

    darkbridge convert landscape.NEF

Same as above but converting all the sidecar files in the current directory.::

    darkbridge convert ./*.NEF

List metadata of image files the current directory and all subdirectory
with a verbosity level to show field names and contents::

    darkbridge -vv list --recursive ./*.NEF

Search images files with the metadata ``dc:subject`` entered::

    darkbridge -vv  search -m 'dc:subject' ./*.NEF

Same as above but with a more permisive pattern (i.e. all fields of 'dc'
family will be displayed::

    darkbridge -vv  search -m 'dc:' ./*.NEF

Show the images adjustement ``nikon::PictureControl`` of a particular image
files. Search may be used on a selection of files or one file::

    darkbridge -vv  search -p nikon::PictureControl landscape.NEF

Same as above but with a more permisive pattern (i.e. all image adjustement
relative to noise will be displayed::

    darkbridge -vv  search -p Noise landscape.NEF

