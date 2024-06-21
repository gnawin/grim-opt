#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from typing import Tuple, List

import numpy as np
import numpy.ma as ma
import pandas as pd
import geojson
import pyproj
import matplotlib.path as mp
from netCDF4 import Dataset
from shapely.geometry import Polygon
from scipy import ndimage

from grim_opt.config import LandCoverPaths
from grim_opt.config_defaults import config_land_cover_default
from grim_opt.helpers import get_region_names_list, get_region_poly


def perform_land_cover(
        paths: LandCoverPaths,
        out_shp: Tuple[int, int], r: int, class_artificial_indices: List[int]
        ):
    """
    Perform the pre-processing step in which the table of area per region per land cover class is generated

    :param paths Struct with all the filepaths (input and output) needed for this processing step
    :type paths LandCoverPaths

    :param out_shp: Output array shape (two-dimensional)
    :type out_shp: Tuple[int, int]
    :param r: Radius of circles
    :type r: int
    :param class_artificial_indices: Exclude land cover class:artificial surfaces

    :return:
    """
    # First read all the file inputs into datasets
    nc_data = Dataset(paths.corine_land_cover, 'r')

    region_polys = get_region_poly(paths.gis_nlregions, paths.region_names)  # read region polygons in json format
    region_names_list = get_region_names_list(paths.region_names)  # read a list of region names

    json_file = open(paths.exclusion_poly, 'r+', encoding='utf-8')  # this is a special polygon

    # coordinate transforms (projection)
    EPSG3035 = pyproj.Proj("EPSG:3035")  # Was +init=EPSG:3035, library DeprecationWarning forced change
    EPSG4326 = pyproj.Proj("EPSG:4326")  # Was +init=EPSG:4326, library DeprecationWarning forced change

    row_names = [1, 2, 3, 7, 8, 9, 12, 15, 16, 18, 20, 21, 23, 24, 25, 26, 27, 29, 30, 32, 35, 36, 37]

    # mask unavailable points
    land_cover_unmasked = np.array(nc_data['data'])
    land_cover_masked = ma.masked_array(land_cover_unmasked, fill_value=False)
    y = np.array(nc_data['y'])  # with dimension y.shape
    x = np.array(nc_data['x'])  # with dimension x.shape

    # coordinate transformation
    # pyproj requires same dimension
    # create a meshgrid based on x, y
    xg, yg = np.meshgrid(x, y)
    lon, lat = pyproj.transform(EPSG3035, EPSG4326, xg, yg)

    # from lon, lat meshgrid to points with (lon,lat)
    points = np.array((lon.flatten(), lat.flatten())).transpose()

    # polygon Veluwe
    poly = geojson.load(json_file)
    poly_veluwe = np.squeeze(np.array(poly["coordinates"]))
    exterior_veluwe = Polygon(poly_veluwe).buffer(0).exterior.coords[:]
    boolean_veluwe = mp.Path(np.asarray(exterior_veluwe)).contains_points(points).reshape(y.size, x.size)  # inside True

    # exclude land cover class:artificial surfaces
    invalid_ = np.in1d(land_cover_masked[:][:], class_artificial_indices)
    invalid = invalid_.reshape(y.size, x.size)

    # find the indice of these points
    result = np.where(invalid)
    points_indice = list(zip(result[0], result[1]))

    maskcenters = np.asarray(points_indice)

    # Get a disk kernel
    X, Y = [np.arange(-r, r+1)]*2
    disk_mask = X[:, None]**2 + Y**2 <= r*r
    # Ridx, Cidx = np.where(disk_mask)  # TODO: is this used? when?

    # Initialize output array and set the maskcenters as 1s
    out = np.zeros(out_shp, dtype=bool)
    out[maskcenters[:, 0], maskcenters[:, 1]] = 1

    # Use binary dilation to get the desired output
    out = ndimage.binary_dilation(out, disk_mask)

    land_cover_masked.mask = out | land_cover_masked.mask

    # create a dataframe to storedata
    df = pd.DataFrame(columns=np.arange(30), index=row_names)

    for key, value in region_polys.items():
        print(key)
        polygon = value

        region_num = None
        for i, v in enumerate(region_names_list):
            if key == v:
                region_num = i
                break

        print(region_num)

        # points inside the region = True
        boolean_region = mp.Path(polygon.exterior.coords[:]).contains_points(points).reshape(y.size, x.size)

        land_cover_region = land_cover_masked.copy()
        land_cover_region.mask = ~boolean_region | boolean_veluwe | land_cover_masked.mask

        for i in np.arange(len(row_names)):
            df.loc[row_names[i]][region_num] = np.count_nonzero(land_cover_region == row_names[i])

    # noinspection PyTypeChecker
    df.to_csv(path_or_buf=paths.region_area_land_cover)


def default_perform_land_cover():
    perform_land_cover(
        paths=config_land_cover_default.paths,
        out_shp=config_land_cover_default.out_shp,
        r=config_land_cover_default.r,
        class_artificial_indices=config_land_cover_default.class_artificial_indices,
    )


if __name__ == '__main__':
    default_perform_land_cover()

