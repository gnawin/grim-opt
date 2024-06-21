#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import numpy as np
from matplotlib import cm
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import grim_opt.path_helpers as ps


plt.switch_backend('agg')


path_df_gen_noCap = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, 'no')
path_df_gen_20 = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, '20')
path_df_gen_50 = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, '50')
path_df_gen_80 = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, '80')
path_df_gen_100 = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_GENCAP_RENEW, '100')

path_df_trans_noCap = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_TRANSCAP_RENEW, 'no')
path_df_trans_20pct = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_TRANSCAP_RENEW, '20')
path_df_trans_50pct = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_TRANSCAP_RENEW, '50')
path_df_trans_80pct = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_TRANSCAP_RENEW, '80')
path_df_trans_100pct = ps.mkdefaultpath_arg(ps.DEFAULT_EXP_ROOT, ps.FileID.OPTIMIZED_TRANSCAP_RENEW, '100')

path_plot_capacities_totals = ps.mkdefaultpath(ps.DEFAULT_EXP_ROOT, ps.FileID.PLOT_CAPACITIES_TOTALS)


df_gen_noCap = pd.read_csv(path_df_gen_noCap, index_col=0)
df_gen_20 = pd.read_csv(path_df_gen_20, index_col=0)
df_gen_50 = pd.read_csv(path_df_gen_50, index_col=0)
df_gen_80 = pd.read_csv(path_df_gen_80, index_col=0)
df_gen_100 = pd.read_csv(path_df_gen_100, index_col=0)

df_trans_noCap = pd.read_csv(path_df_trans_noCap, index_col=0)
df_trans_20pct = pd.read_csv(path_df_trans_20pct, index_col=0)
df_trans_50pct = pd.read_csv(path_df_trans_50pct, index_col=0)
df_trans_80pct = pd.read_csv(path_df_trans_80pct, index_col=0)
df_trans_100pct = pd.read_csv(path_df_trans_100pct, index_col=0)

df_gen_noCap = df_gen_noCap.sum(axis=1)
df_gen_20 = df_gen_20.sum(axis=1)
df_gen_50 = df_gen_50.sum(axis=1)
df_gen_80 = df_gen_80.sum(axis=1)
df_gen_100 = df_gen_100.sum(axis=1)


df_transmission = pd.Series(
    np.array([
        df_trans_noCap.sum(axis=1).sum(),
        df_trans_20pct.sum(axis=1).sum(),
        df_trans_50pct.sum(axis=1).sum(),
        df_trans_80pct.sum(axis=1).sum(),
        df_trans_100pct.sum(axis=1).sum(),
    ]),
    index=['noCap', '20%', '50%', '80%', '100%'],
)

wind = np.array([
    df_gen_noCap['wind'],
    df_gen_20['wind'],
    df_gen_50['wind'],
    df_gen_80['wind'],
    df_gen_100['wind']
])

solar = np.array([
    df_gen_noCap['solar'],
    df_gen_20['solar'],
    df_gen_50['solar'],
    df_gen_80['solar'],
    df_gen_100['solar']
])

biomass = np.array([
    df_gen_noCap['biomass'],
    df_gen_20['biomass'],
    df_gen_50['biomass'],
    df_gen_80['biomass'],
    df_gen_100['biomass']
])

CCGT = np.array([
    df_gen_noCap['CCGT'],
    df_gen_20['CCGT'],
    df_gen_50['CCGT'],
    df_gen_80['CCGT'],
    df_gen_100['CCGT']
])

coal = np.array([
    df_gen_noCap['coal'],
    df_gen_20['coal'],
    df_gen_50['coal'],
    df_gen_80['coal'],
    df_gen_100['coal']
])

FBConversion = np.array([
    df_gen_noCap['battery'],
    df_gen_20['battery'],
    df_gen_50['battery'],
    df_gen_80['battery'],
    df_gen_100['battery']
])

H2Conversion = np.array([
    df_gen_noCap['hydrogen'],
    df_gen_20['hydrogen'],
    df_gen_50['hydrogen'],
    df_gen_80['hydrogen'],
    df_gen_100['hydrogen']
])

transmission = np.array([
    df_transmission['noCap'],
    df_transmission['20%'],
    df_transmission['50%'],
    df_transmission['80%'],
    df_transmission['100%']
])


r = np.arange(5)

fig = plt.figure(figsize=(20, 10))
Blues = cm.get_cmap('Blues')

p1 = plt.bar(
    r, wind,
    color=Blues(0.56),
)

p2 = plt.bar(
    r, solar,
    bottom=wind,
    color='Red',
)

p3 = plt.bar(
    r, biomass,
    bottom=wind + solar,
    color='Green',
)

p4 = plt.bar(
    r, coal,
    bottom=wind + solar + biomass,
    color='rebeccapurple',
)

p5 = plt.bar(
    r, CCGT,
    bottom=wind + solar + biomass + coal,
    color='Grey',
)

p6 = plt.bar(
    r, FBConversion,
    bottom=wind + solar + biomass + CCGT + coal,
    color='brown',
)

p7 = plt.bar(
    r, H2Conversion,
    bottom=wind + solar + biomass + CCGT + coal + FBConversion,
    color='orange',
)

p8 = plt.bar(
    r, transmission,
    bottom=wind + solar + biomass + CCGT + coal + FBConversion + H2Conversion,
    color='silver',
)

names = np.array(['0%', '20%', '50%', '80%', '100%'])

plt.xticks(r, names, fontsize=20)
plt.yticks(fontsize=20)
plt.ylabel('Total installed capacity (MW)', fontsize=25)
plt.xlabel('RES share', fontsize=25)
# plt.title('LCOE', fontsize=20)
plt.legend(
    (p1, p2, p3, p4, p5, p6, p7, p8),
    ('Onshore Wind', 'Solar PV', 'Biomass', 'Coal', 'CCGT', 'Flow Battery Conversion', 'Hydrogen Conversion', 'Network'),
    fontsize=18
)
# plt.ylim(ymax=4)
sns.despine()
plt.savefig(path_plot_capacities_totals, bbox_inches='tight')
