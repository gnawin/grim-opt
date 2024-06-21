#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
Definitions (classes) for all configuration arguments used in the different processing steps of GRIM.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from grim_opt.path_helpers import mkdefaultpath, FileID, mkdefaultpath_arg


@dataclass
class LandCoverPaths:
    corine_land_cover: Path
    region_names: Path
    gis_nlregions: Path
    exclusion_poly: Path
    region_area_land_cover: Path  # output

    @staticmethod
    def convention_paths_experiment_root(experiment: Path):
        return LandCoverPaths(
            corine_land_cover=mkdefaultpath(experiment, FileID.CORINE_LAND_COVER),
            region_names=mkdefaultpath(experiment, FileID.REGION_NAMES),
            gis_nlregions=mkdefaultpath(experiment, FileID.POLYGONS_BASE),
            exclusion_poly=mkdefaultpath(experiment, FileID.POLYGONS_EXCLUSION),
            region_area_land_cover=mkdefaultpath(experiment, FileID.REGION_AREA_LAND_COVER_CLASSES),
        )


@dataclass
class OptimizationPaths:
    region_area_generation: Path
    params_techno_econ: Path
    gencap_existing: Path
    transcap_connections: Path
    electricity_demand: Path
    electricity_gencap_factors_new_wind: Path
    electricity_gencap_factors_new_solar: Path
    optimized_gencap_renew: Path  # output
    optimized_transcap_renew: Path  # output

    @staticmethod
    def convention_paths_experiment_root(experiment: Path, omega: float):
        return OptimizationPaths(
            region_area_generation=mkdefaultpath(experiment, FileID.REGION_AREA_GENERATION),
            params_techno_econ=mkdefaultpath(experiment, FileID.PARAMETERS_TECHNO_ECON),
            gencap_existing=mkdefaultpath(experiment, FileID.ELECTRICITY_GENCAP_EXISTING),
            transcap_connections=mkdefaultpath(experiment, FileID.ELECTRICITY_TRANSCAP_CONNECTIONS),

            electricity_demand=mkdefaultpath(experiment, FileID.ELECTRICITY_DEMAND),
            electricity_gencap_factors_new_wind=mkdefaultpath(experiment, FileID.ELECTRICITY_GENCAP_FACTORS_NEW_WIND),
            electricity_gencap_factors_new_solar=mkdefaultpath(experiment, FileID.ELECTRICITY_GENCAP_FACTORS_NEW_SOLAR),
            optimized_gencap_renew=mkdefaultpath_arg(experiment, FileID.OPTIMIZED_GENCAP_RENEW, f'{int(omega * 100)}'),
            optimized_transcap_renew=mkdefaultpath_arg(experiment, FileID.OPTIMIZED_TRANSCAP_RENEW, f'{int(omega * 100)}'),
        )


@dataclass
class SolverParams:
    name: str
    crossover: Optional[int]
    method: Optional[int]
    threads: Optional[int]


@dataclass
class EnergyTechParams:
    N: np.ndarray
    FL: np.ndarray

    G: List[str]
    """
    Needs to be in the set consisting of A2-A6, A9 from parameters_techno_econ (onshore, solar, gas, biomass, coal, offshore)
    """
    SC: List[str]
    """
    Needs to be in the set consisting of A7, A8 from parameters_techno_econ (battery, hydrogen)
    """
    RES: List[str]
    """
    Subset of A2, A3, A5, A9 (onshore, solar, biomass, offshore), also a subset of G 
    """
    non_VRES: List[str]
    """
    G - RES
    """

@dataclass
class OptOtherParams:
    lol: float
    """
    int > 0
    """
    R: int
    """
    1 <= int <= denominator_R
    """
    denominator_R: int
    """
    = 8760, this is not something you want to change
    """
    T: np.ndarray
    """
    np.arrange[0, R]     
    """
    T2: np.ndarray
    """
    np.arrange[1, R]     
    """    
    CT: float
    """
    float > 0      
    """    
    r: float
    """
    0 < float < 1     
    """        
    LT: int
    """
    needs to be in column F under the header "Lifetime(yr)" from parameters_techno_econ      
    """        
    reserve_margin: float
    """
    0<= float
    """
    omega: float
    """
    0<= float <=1
    """
    e_l: float
    """
    0<= float <=1
    """

@dataclass
class ConfigLandCover:
    paths: LandCoverPaths
    out_shp: Tuple[int, int]
    r: int
    class_artificial_indices: List[int]


@dataclass
class ConfigOptimization:
    paths: OptimizationPaths
    et_params: EnergyTechParams
    solver_params: SolverParams
    num_rows_cost_params: int
    other_params: OptOtherParams
