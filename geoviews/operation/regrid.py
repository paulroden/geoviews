import param
import numpy as np
import xarray as xr

from holoviews.core.util import get_param_values
from holoviews.element import Image as HvImage
from holoviews.operation.datashader import regrid

from ..element import Image, is_geographic


class weighted_regrid(regrid):
    """
    Implements weighted regridding of rectilinear and curvilinear
    grids using the xESMF library, supporting all the ESMF regridding
    algorithms including bilinear, conservative and nearest neighbour
    regridding. In addition to these different interpolation options
    it supports
    """

    interpolation = param.ObjectSelector(default='bilinear',
        objects=['bilinear', 'conservative', 'nearest_s2d', 'nearest_d2s'], doc="""
        Interpolation method""")

    reuse_weights = param.Boolean(default=True, doc="""
        Whether the sparse regridding weights should be cached as a local
        NetCDF file in the path defined by the file_pattern parameter.
        Can provide considerable speedups when exploring a larger dataset.""")

    file_pattern = param.String(default='{method}_{x_range}_{y_range}_{width}x{height}.nc',
                                doc="""
        The file pattern used to store the regridding weights when the
        reuse_weights parameter is disabled. Note the files are not
        cleared automatically so make sure you clean up the cached
        files when you are done.""")

    def _get_regridder(self, element):
        try:
            import xesmf as xe
        except:
            raise ImportError("xESMF library required for weighted regridding.")
        x, y = element.kdims
        info = self._get_sampling(element, x, y)
        (x_range, y_range), _, (width, height), (xtype, ytype) = info
        if x_range[0] > x_range[1]:
            x_range = x_range[::-1]
        element = element.select(**{x.name: x_range, y.name: y_range})
        irregular = any(element.interface.irregular(element, d)
                        for d in [x, y])
        coord_opts = {'flat': False} if irregular else {'expanded': False}
        coords = tuple(element.dimension_values(d, **coord_opts)
                       for d in [x, y])
        arrays = self._get_xarrays(element, coords, xtype, ytype)
        ys = np.linspace(y_range[0], y_range[1], height)
        xs = np.linspace(x_range[0], x_range[1], width)
        ds_out = xr.Dataset({'lat': ys, 'lon': xs})
        ds = xr.Dataset(arrays)
        ds.rename({x.name: 'lon', y.name: 'lat'}, inplace=True)

        x_range = str(tuple('%.3f' % r for r in x_range)).replace("'", '')
        y_range = str(tuple('%.3f' % r for r in y_range)).replace("'", '')
        filename = self.file_pattern.format(method=self.p.interpolation,
                                            width=width, height=height,
                                            x_range=x_range, y_range=y_range)
        regridder = xe.Regridder(ds, ds_out, self.p.interpolation,
                                 reuse_weights=self.p.reuse_weights,
                                 filename=filename.replace(', ', '_'))
        return regridder, arrays


    def _process(self, element, key=None):
        regridder, arrays = self._get_regridder(element)
        ds = xr.Dataset({vd: regridder(arr) for vd, arr in arrays.items()})
        params = dict(get_param_values(element), kdims=['lon', 'lat'])
        if is_geographic(element):
            return Image(ds, crs=element.crs, **params)
        return HvImage(ds, **params)
