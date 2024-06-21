#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import grim_opt.helpers as hp
import grim_opt.path_helpers as ps


plt.switch_backend('agg')

path_region_names = ps.mkdefaultpath(ps.DEFAULT_EXP_ROOT, ps.FileID.REGION_NAMES)
path_gis_nlregions = ps.mkdefaultpath(ps.DEFAULT_EXP_ROOT, ps.FileID.POLYGONS_BASE)

path_noCap = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, 'no')
path_geno_20 = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, '20')
path_geno_50 = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, '50')
path_geno_80 = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, '80')
path_geno_100 = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, '100')

path_plot_capacities_regions = ps.mkdefaultpath(ps.DEFAULT_EXP_ROOT, ps.FileID.PLOT_CAPACITIES_REGIONS)

cols = ["Onshore Wind(MW)", "Onshore Wind fraction", "Solar PV(MW)", "Solar PV fraction", "Biomass(MW)", "Coal(MW)", "CCGT(MW)"]
rows = ["0% RES", "20% RES", "50% RES", "80% RES", "100% RES"]


noCap = pd.read_csv(path_noCap, index_col=0)
geno_20 = pd.read_csv(path_geno_20, index_col=0)
geno_50 = pd.read_csv(path_geno_50, index_col=0)
geno_80 = pd.read_csv(path_geno_80, index_col=0)
geno_100 = pd.read_csv(path_geno_100, index_col=0)

max_c = pd.read_csv(ps.mkdefaultpath(ps.DEFAULT_EXP_ROOT, ps.FileID.REGION_AREA_GENERATION), index_col=0)

region_polys = hp.get_region_poly(path_gis_nlregions, path_region_names)
region_names_list = hp.get_region_names_list(path_region_names)

# plot
# fig = plt.figure(figsize=(20, 20))
fig, axes = plt.subplots(nrows=5, ncols=7, figsize=(40, 25))

for ax, col in zip(axes[0], cols):
    ax.set_title(col, size=20, weight='bold')

for ax, row in zip(axes[:, 0], rows):
    ax.text(-0.5, 0.5, row, transform=ax.transAxes, size=20, weight='bold')

[axi.set_axis_off() for axi in axes.ravel()]

# noCap
ax = fig.add_subplot(5, 7, 1)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: noCap.loc["wind", :][k] for k, v in enumerate(region_names_list)}  # TODO: change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(vmin=min(colvals), vmax=max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)  # TODO: change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

# cbar.ax.set_yticklabels(ticks)
# cbar.update_ticks()
# plt.title('Wind') # change this line

ax = fig.add_subplot(5, 7, 2)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

# TODO: change this line
region = {v: noCap.loc["wind", :][k] / max_c.loc[k]["Max_wind"] for k, v in enumerate(region_names_list)}
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(vmin=0, vmax=1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
# sm.set_clim(vmin=0, vmax=1) # change this line
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Wind') # change this line

# subplot
ax = fig.add_subplot(5, 7, 3)  # TODO: change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # TODO: change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Solar') # change this line

ax = fig.add_subplot(5, 7, 4)  # TODO: change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # TODO: change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# sm.set_clim(vmin=0, vmax=1) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

ax = fig.add_subplot(5, 7, 5)  # TODO: change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # TODO: change this line
colvals = region.values()

cmap = plt.cm.Greens
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

# subplot
ax = fig.add_subplot(5, 7, 6)  # TODO: change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49, resolution="c"
)

region = {v: noCap.loc["coal", :][k] for k, v in enumerate(region_names_list)}  # TODO: change this line
colvals = region.values()

cmap = plt.cm.Purples
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000)  # TODO: change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Coal')  # TODO: change this line

# subplot
ax = fig.add_subplot(5, 7, 7)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49, resolution="c"
)

region = {v: noCap.loc["CCGT", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greys
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('CCGT') # change this line


# 20%
ax = fig.add_subplot(5, 7, 8)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_20.loc["wind", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Wind') # change this line


ax = fig.add_subplot(5, 7, 9)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49, resolution="c"
)

region = {v: geno_20.loc["wind", :][k] / max_c.loc[k]["Max_wind"] for k, v in
          enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

# subplot
ax = fig.add_subplot(5, 7, 10)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Solar') # change this line


# subplot
ax = fig.add_subplot(5, 7, 11)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49, resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

ax = fig.add_subplot(5, 7, 12)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greens
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

# subplot
ax = fig.add_subplot(5, 7, 13)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_20.loc["coal", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Purples
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Coal') # change this line

# subplot
ax = fig.add_subplot(5, 7, 14)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_20.loc["CCGT", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greys
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('CCGT') # change this line


# 50%
ax = fig.add_subplot(5, 7, 15)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_50.loc["wind", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Wind') # change this line

ax = fig.add_subplot(5, 7, 16)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_50.loc["wind", :][k] / max_c.loc[k]["Max_wind"] for k, v in
          enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

# subplot
ax = fig.add_subplot(5, 7, 17)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_50.loc["solar", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Solar') # change this line


ax = fig.add_subplot(5, 7, 18)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_50.loc["solar", :][k] / max_c.loc[k]["Max_solar"] for k, v in
          enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

ax = fig.add_subplot(5, 7, 19)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greens
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

# subplot
ax = fig.add_subplot(5, 7, 20)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_50.loc["coal", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Purples
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Coal') # change this line

# subplot
ax = fig.add_subplot(5, 7, 21)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_50.loc["CCGT", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greys
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('CCGT') # change this line


# 80%
ax = fig.add_subplot(5, 7, 22)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_80.loc["wind", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Wind') # change this line

ax = fig.add_subplot(5, 7, 23)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_80.loc["wind", :][k] / max_c.loc[k]["Max_wind"] for k, v in
          enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Wind') # change this line


# subplot
ax = fig.add_subplot(5, 7, 24)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_80.loc["solar", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Solar') # change this line


ax = fig.add_subplot(5, 7, 25)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_80.loc["solar", :][k] / max_c.loc[k]["Max_solar"] for k, v in
          enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

ax = fig.add_subplot(5, 7, 26)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_80.loc["biomass", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greens
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

# subplot
ax = fig.add_subplot(5, 7, 27)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_80.loc["coal", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Purples
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Coal') # change this line

# subplot
ax = fig.add_subplot(5, 7, 28)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_80.loc["CCGT", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greys
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('CCGT') # change this line


# 100%
ax = fig.add_subplot(5, 7, 29)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_100.loc["wind", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Wind') # change this line

ax = fig.add_subplot(5, 7, 30)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_100.loc["wind", :][k] / max_c.loc[k]["Max_wind"] for k, v in
          enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Blues
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Wind') # change this line


# subplot
ax = fig.add_subplot(5, 7, 31)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_100.loc["solar", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Solar') # change this line

ax = fig.add_subplot(5, 7, 32)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_100.loc["solar", :][k] / max_c.loc[k]["Max_solar"] for k, v in
          enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Reds
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

ax = fig.add_subplot(5, 7, 33)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: geno_100.loc["biomass", :][k] for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greens
norm = plt.Normalize(min(colvals), max(colvals))
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(min(colvals), max(colvals), 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)

# subplot
ax = fig.add_subplot(5, 7, 34)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Purples
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Coal') # change this line

# subplot
ax = fig.add_subplot(5, 7, 35)  # change this line

baseMap = Basemap(
    projection="merc",
    llcrnrlat=50.62, urcrnrlat=53.72,
    llcrnrlon=3.25, urcrnrlon=7.49,
    resolution="c"
)

region = {v: 0 for k, v in enumerate(region_names_list)}  # change this line
colvals = region.values()

cmap = plt.cm.Greys
norm = plt.Normalize(0, 1)
patches = []

for name in region_names_list:
    xy = np.squeeze(np.array(region_polys[name].exterior.coords[:]))
    x_proj, y_proj = baseMap(xy[:, 0], xy[:, 1])
    ax.plot(x_proj, y_proj, color="black")
    color = cmap(norm(region[name]))
    patches.append(Polygon(np.array(list(zip(x_proj, y_proj))), True, color=color))

baseMap.drawcountries(color="white")
baseMap.drawcoastlines(color="white")
ax.add_collection(PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2))

sm = plt.cm.ScalarMappable(cmap=cmap)
# plt.cm.ScalarMappable(cmap=cmap, norm=norm).set_clim(vmin=0, vmax=9000) # change this line
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
ticks = np.linspace(0, 1, 6)
cbar.set_ticks(ticks)
cbar.ax.tick_params(labelsize=15)
# plt.title('Coal') # change this line

plt.savefig(path_plot_capacities_regions, bbox_inches='tight', dpi=200)
