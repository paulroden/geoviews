import param
from .element import (_Element, Feature, Tiles,     # noqa (API import)
                      WMTS, LineContours, FilledContours, Text, Image,
                      Points, Path, Polygons, Shape, Dataset, RGB,
                      Contours, Graph, TriMesh, Nodes, EdgePaths,
                      QuadMesh, VectorField, HexTiles, Labels)
from . import data                                  # noqa (API import)
from . import operation                             # noqa (API import)
from . import plotting                              # noqa (API import)
from . import feature                               # noqa (API import)


__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                              reponame="geoviews"))


# make pyct's example/data commands available if possible
from functools import partial
try:
    from pvutil.cmd import copy_examples as _copy, fetch_data as _fetch, examples as _examples
    copy_examples = partial(_copy,'geoviews')
    fetch_data = partial(_fetch,'geoviews')
    examples = partial(_examples,'geoviews')
except ImportError:
    def _missing_cmd(*args,**kw): return("install pyct to enable this command (e.g. `conda install pyct`)")
    _copy = _fetch = _examples = _missing_cmd
    def err(): raise ValueError(_missing_cmd())
    fetch_data = copy_examples = examples = err
del partial, _examples, _copy, _fetch
