#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
Default values for all configuration arguments used in the different processing steps of GRIM.
"""
import numpy as np

from grim_opt.path_helpers import DEFAULT_EXP_ROOT
from grim_opt.config import SolverParams, EnergyTechParams, LandCoverPaths, OptimizationPaths, OptOtherParams, ConfigLandCover, \
    ConfigOptimization


config_land_cover_default = ConfigLandCover(
    paths=LandCoverPaths.convention_paths_experiment_root(DEFAULT_EXP_ROOT),
    out_shp=(4721, 4412),
    r=0,
    class_artificial_indices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
)


def opt_paths_default(omega: float):
    return OptimizationPaths.convention_paths_experiment_root(DEFAULT_EXP_ROOT, omega)


et_params_default = EnergyTechParams(
    N=np.arange(32),
    FL=np.arange(50),
    G=['onshore', 'solar', 'biomass', 'gas'],
    SC=['battery', 'hydrogen'],
    RES=['onshore', 'solar', 'biomass'],
    non_VRES=['biomass', 'gas'],
)

solver_params_default = SolverParams(
    name='glpk',
    crossover=None,
    method=None,
    threads=None,  # other possibility: 8
)

opt_R_default = 1
opt_otherparams_default = OptOtherParams(
    lol=23000,
    R=opt_R_default,
    denominator_R=8760,
    T=np.arange(0, opt_R_default),
    T2=np.arange(1, opt_R_default),
    CT=10000,
    r=0.05,
    LT=40,
    reserve_margin=0.5,
    omega=1.0,
    e_l=0.25,
)


config_optimization_default = ConfigOptimization(
    paths=opt_paths_default(opt_otherparams_default.omega),
    et_params=et_params_default,
    solver_params=solver_params_default,
    num_rows_cost_params=1000,
    other_params=opt_otherparams_default,
)
