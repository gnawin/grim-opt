#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import yaml

from grim_opt.path_helpers import mkdefaultrelpath, FileID
from grim_opt.config import ConfigLandCover, ConfigOptimization, LandCoverPaths, SolverParams, EnergyTechParams, \
    OptOtherParams, OptimizationPaths
import grim_opt.config_defaults as defs


def read_from_yaml(cfg_path: Path) -> Tuple[Optional[ConfigLandCover], Optional[ConfigOptimization]]:
    cfg_file = cfg_path.resolve()
    cfg_file_dir = cfg_file.parent

    with open(cfg_file, 'r') as cfg_yaml:
        cfg_dict = yaml.load(cfg_yaml, Loader=yaml.FullLoader)

    cfg_land_cover: Optional[ConfigLandCover] = None
    if 'land_cover' in cfg_dict:
        cfg_land_cover = __parse_cfg_land_cover(cfg_dict['land_cover'], cfg_file_dir)

    cfg_optimization: Optional[ConfigOptimization] = None
    if 'optimization' in cfg_dict:
        cfg_optimization = __parse_cfg_optimization(cfg_dict['optimization'], cfg_file_dir)

    return cfg_land_cover, cfg_optimization


def __parse_cfg_land_cover(dict_land_cover: dict, exp_root: Path) -> ConfigLandCover:
    # The absence of a 'paths' key means we wish FULLY DEFAULT paths
    paths = LandCoverPaths.convention_paths_experiment_root(exp_root)
    if 'paths' in dict_land_cover:
        paths_dict = dict_land_cover['paths']
        # Otherwise, the elements of the 'paths' section should be relative to the folder where this config file sits
        paths = LandCoverPaths(
            corine_land_cover=exp_root / paths_dict.get('corine_land_cover',
                                                        mkdefaultrelpath(FileID.CORINE_LAND_COVER)),
            region_names=exp_root / paths_dict.get('region_names', mkdefaultrelpath(FileID.REGION_NAMES)),
            gis_nlregions=exp_root / paths_dict.get('gis_nlregions', mkdefaultrelpath(FileID.POLYGONS_BASE)),
            exclusion_poly=exp_root / paths_dict.get('exclusion_poly', mkdefaultrelpath(FileID.POLYGONS_EXCLUSION)),
            region_area_land_cover=exp_root / paths_dict.get('region_area_land_cover',
                                                             mkdefaultrelpath(FileID.REGION_AREA_LAND_COVER_CLASSES)),
        )

    out_shp = defs.config_land_cover_default.out_shp
    if 'out_shp' in dict_land_cover:
        out_shp = (dict_land_cover['out_shp']['x'], dict_land_cover['out_shp']['y'])

    r = dict_land_cover.get('r', defs.config_land_cover_default.r)

    class_artificial_indices = dict_land_cover.get('class_artificial_indices', defs.config_land_cover_default.class_artificial_indices)

    return ConfigLandCover(paths=paths, out_shp=out_shp, r=r, class_artificial_indices=class_artificial_indices)


def __parse_cfg_optimization(dict_opt: dict, exp_root: Path) -> ConfigOptimization:
    num_rows_cost_params = dict_opt.get('num_rows_cost_params', defs.config_optimization_default.num_rows_cost_params)

    defs_solver = defs.config_optimization_default.solver_params
    solver_params = defs_solver
    if 'solver_params' in dict_opt:
        dict_solver = dict_opt['solver_params']
        solver_params = SolverParams(
            name=dict_solver.get('name', defs_solver.name),
            crossover=dict_solver.get('crossover', defs_solver.crossover),
            method=dict_solver.get('method', defs_solver.method),
            threads=dict_solver.get('threads', defs_solver.threads),
        )

    defs_et = defs.config_optimization_default.et_params
    et_params = defs_et
    if 'et_params' in dict_opt:
        dict_et = dict_opt['et_params']
        et_params = EnergyTechParams(
            N=np.arange(dict_et['N']) if 'N' in dict_et else defs_et.N,
            FL=np.arange(dict_et['FL']) if 'FL' in dict_et else defs_et.FL,
            G=dict_et.get('G', defs_et.G),
            SC=dict_et.get('SC', defs_et.SC),
            RES=dict_et.get('RES', defs_et.RES),
            non_VRES=dict_et.get('non_VRES', defs_et.non_VRES),
        )

    defs_other = defs.config_optimization_default.other_params
    other_params = defs_other
    if 'other_params' in dict_opt:
        dict_other = dict_opt['other_params']
        built_R=dict_other.get('R', defs_other.R)
        other_params = OptOtherParams(
            lol=dict_other.get('lol', defs_other.lol),
            R=built_R,
            denominator_R=dict_other.get('denominator_R', defs_other.denominator_R),
            T=np.arange(0, built_R),
            T2=np.arange(1, built_R),
            CT=dict_other.get('CT', defs_other.CT),
            r=dict_other.get('r', defs_other.r),
            LT=dict_other.get('LT', defs_other.LT),
            reserve_margin=dict_other.get('reserve_margin', defs_other.reserve_margin),
            omega=dict_other.get('omega', defs_other.omega),
            e_l=dict_other.get('e_l', defs_other.e_l),
        )

    # The absence of a 'paths' key means we wish FULLY DEFAULT paths
    paths = OptimizationPaths.convention_paths_experiment_root(exp_root, other_params.omega)
    if 'paths' in dict_opt:
        paths_dict = dict_opt['paths']
        # Otherwise, the elements of the 'paths' section should be relative to the folder where this config file sits
        paths = OptimizationPaths(
            region_area_generation=exp_root / paths_dict.get('region_area_generation', mkdefaultrelpath(FileID.REGION_AREA_GENERATION)),
            params_techno_econ=exp_root / paths_dict.get('params_techno_econ', mkdefaultrelpath(FileID.PARAMETERS_TECHNO_ECON)),
            gencap_existing=exp_root / paths_dict.get('gencap_existing', mkdefaultrelpath(FileID.ELECTRICITY_GENCAP_EXISTING)),
            transcap_connections=exp_root / paths_dict.get('transcap_connections', mkdefaultrelpath(FileID.ELECTRICITY_TRANSCAP_CONNECTIONS)),
            electricity_demand=exp_root / paths_dict.get('electricity_demand', mkdefaultrelpath(FileID.ELECTRICITY_DEMAND)),
            electricity_gencap_factors_new_wind=exp_root / paths_dict.get('electricity_gencap_factors_new_wind', mkdefaultrelpath(FileID.ELECTRICITY_GENCAP_FACTORS_NEW_WIND)),
            electricity_gencap_factors_new_solar=exp_root / paths_dict.get('electricity_gencap_factors_new_solar', mkdefaultrelpath(FileID.ELECTRICITY_GENCAP_FACTORS_NEW_SOLAR)),
            optimized_gencap_renew=exp_root / paths_dict.get('optimized_gencap_renew', mkdefaultrelpath(FileID.OPTIMIZED_GENCAP_RENEW)),
            optimized_transcap_renew=exp_root / paths_dict.get('optimized_transcap_renew', mkdefaultrelpath(FileID.OPTIMIZED_TRANSCAP_RENEW)),
        )

    return ConfigOptimization(
        paths=paths, et_params=et_params, solver_params=solver_params,
        num_rows_cost_params=num_rows_cost_params, other_params=other_params,
    )
