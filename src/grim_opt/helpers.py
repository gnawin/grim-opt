#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import numpy as np
import geojson
from shapely.geometry import Polygon
import pandas as pd
from shapely.ops import cascaded_union


def get_region_names_list(path_region_names_csv):
    df = pd.read_csv(path_region_names_csv)
    region_names_list = list(df.columns.values)

    return region_names_list


def get_region_component_names(path_region_names_csv):
    df = pd.read_csv(path_region_names_csv)

    region_names = {}

    for column, content in df.iteritems():
        region_names[column] = []
        for row, value in content.iteritems():
            if pd.notnull(value):
                region_names[column].append(value)

    return region_names


def get_region_poly(path_gis_nlregions, path_region_names_csv):
    municipality_polys = {}

    # https://gis.stackexchange.com/questions/93136/how-to-plot-geo-data-using-matplotlib-python
    json_file = open(path_gis_nlregions, "r+", encoding="utf-8")
    poly = geojson.load(json_file)

    # create municipality polygons
    i = 0
    while i < np.array(poly["features"]).size:
        if np.array(poly["features"][i]["geometry"]["coordinates"]).size != 2:
            xy = np.squeeze(np.asarray(poly[i]["geometry"]["coordinates"]))
            municipality_polys[poly["features"][i]["properties"]["name"]] = xy
        i += 1

    # create region names
    region_names = get_region_component_names(path_region_names_csv)

    # merge
    region_polys = {}
    count = 0
    for key, value in region_names.items():
        region_polys[key] = []
        i = 0
        polygons = Polygon()

        if key == "Groningen":
            polygons = Polygon(municipality_polys["Groningen"])

        elif key == "Hoeksewaard":
            polygons = Polygon(municipality_polys["Hoeksche_Waard"])

        else:
            while i < len(value):
                noMatch = 0
                for key1, value1 in municipality_polys.items():
                    if value[i] == key1:
                        polygon1 = Polygon(value1)
                        polygon1 = polygon1.buffer(0)
                        polygons = cascaded_union([polygon1, polygons])
                        polygons = polygons.buffer(0)
                        noMatch = 1
                        break
                if noMatch == 0:
                    count += 1
                    print(value[i])
                i += 1

        region_polys[key] = polygons

#    print("Missing municipalities = ", count)

    return region_polys
