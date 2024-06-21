#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from enum import Enum, unique, auto
from pathlib import Path


PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLE_EXPS_ROOT = PROJECT_ROOT_DIR / 'example-experiments'
DEFAULT_EXP_ROOT = EXAMPLE_EXPS_ROOT / '000-default'


@unique
class FileCategory(Enum):
    FILE_INPUT = auto()
    FILE_OUTPUT = auto()

    def default_subdirname(self):
        return {
            self.FILE_INPUT: Path('inputs'),
            self.FILE_OUTPUT: Path('outputs'),
        }[self]


@unique
class FileID(Enum):
    CORINE_LAND_COVER = auto()
    POLYGONS_BASE = auto()
    POLYGONS_EXCLUSION = auto()
    REGION_NAMES = auto()
    ELECTRICITY_GENCAP_EXISTING = auto()
    ELECTRICITY_TRANSCAP_CONNECTIONS = auto()
    REGION_AREA_LAND_COVER_CLASSES = auto()
    PARAMETERS_TECHNO_ECON = auto()
    REGION_AREA_GENERATION = auto()
    ELECTRICITY_DEMAND = auto()
    ELECTRICITY_GENCAP_FACTORS_NEW_SOLAR = auto()
    ELECTRICITY_GENCAP_FACTORS_NEW_WIND = auto()
    OPTIMIZED_GENCAP_RENEW = auto()
    OPTIMIZED_TRANSCAP_RENEW = auto()
    PLOT_CAPACITIES_TOTALS = auto()
    PLOT_CAPACITIES_REGIONS = auto()

    def category(self):
        return {
            self.CORINE_LAND_COVER: FileCategory.FILE_INPUT,
            self.POLYGONS_BASE: FileCategory.FILE_INPUT,
            self.POLYGONS_EXCLUSION: FileCategory.FILE_INPUT,
            self.REGION_NAMES: FileCategory.FILE_INPUT,
            self.ELECTRICITY_GENCAP_EXISTING: FileCategory.FILE_INPUT,
            self.ELECTRICITY_TRANSCAP_CONNECTIONS: FileCategory.FILE_INPUT,
            self.REGION_AREA_LAND_COVER_CLASSES: FileCategory.FILE_OUTPUT,
            self.PARAMETERS_TECHNO_ECON: FileCategory.FILE_INPUT,
            self.REGION_AREA_GENERATION: FileCategory.FILE_OUTPUT,
            self.ELECTRICITY_DEMAND: FileCategory.FILE_INPUT,
            self.ELECTRICITY_GENCAP_FACTORS_NEW_SOLAR: FileCategory.FILE_INPUT,
            self.ELECTRICITY_GENCAP_FACTORS_NEW_WIND: FileCategory.FILE_INPUT,
            self.OPTIMIZED_GENCAP_RENEW: FileCategory.FILE_OUTPUT,
            self.OPTIMIZED_TRANSCAP_RENEW: FileCategory.FILE_OUTPUT,
            self.PLOT_CAPACITIES_TOTALS: FileCategory.FILE_OUTPUT,
            self.PLOT_CAPACITIES_REGIONS: FileCategory.FILE_OUTPUT,
        }[self]

    def defaultfilename(self):
        return {
            self.CORINE_LAND_COVER: 'corine_land_cover__g100_clc12_V18_5_NL.nc',
            self.POLYGONS_BASE: 'polygons__export.geojson',
            self.POLYGONS_EXCLUSION: 'polygons__veluwe_simplified.geojson',
            self.REGION_NAMES: 'region_names.csv',
            self.ELECTRICITY_GENCAP_EXISTING: 'electricity_gencap_existing.xlsx',
            self.ELECTRICITY_TRANSCAP_CONNECTIONS: 'electricity_transcap_connections.csv',
            self.REGION_AREA_LAND_COVER_CLASSES: 'region_area_land_cover_classes.csv',
            self.PARAMETERS_TECHNO_ECON: 'parameters_techno_econ.xlsx',
            self.REGION_AREA_GENERATION: 'region_area_generation.csv',
            self.ELECTRICITY_DEMAND: 'electricity_demand__medium.csv',
            self.ELECTRICITY_GENCAP_FACTORS_NEW_WIND: 'electricity_gencap_factors_new_wind.csv',
            self.ELECTRICITY_GENCAP_FACTORS_NEW_SOLAR: 'electricity_gencap_factors_new_solar.csv',
            self.OPTIMIZED_GENCAP_RENEW: (lambda pct: f'optimized_gencap_{pct}%_renew.csv'),
            self.OPTIMIZED_TRANSCAP_RENEW: (lambda pct: f'optimized_transcap_{pct}%_renew.csv'),
            self.PLOT_CAPACITIES_TOTALS: 'plot_capacities_totals.png',
            self.PLOT_CAPACITIES_REGIONS: 'plot_capacities_regions.png',
        }[self]


def mkdefaultrelpath(item: FileID, arg=None) -> Path:
    category = item.category()
    filename = item.defaultfilename() if arg is None else item.defaultfilename()(arg)
    cat_subdirname = category.default_subdirname()

    return cat_subdirname / filename

def mkdefaultpath(experiment: Path, item: FileID) -> Path:
    return experiment / mkdefaultrelpath(item)

def mkdefaultpath_arg(experiment: Path, item: FileID, arg: str) -> Path:
    return experiment / mkdefaultrelpath(item, arg)
