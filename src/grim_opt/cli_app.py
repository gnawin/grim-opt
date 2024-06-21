#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import argparse
from pathlib import Path

from grim_opt.config_parse import read_from_yaml
from grim_opt.land_cover import perform_land_cover
from grim_opt.optimization import perform_optimization


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to scenario config file (default: \'./config.yaml\')')

    args = parser.parse_args()

    default_cfg_filename = 'config.yaml'
    default_cfg_path = Path() / default_cfg_filename

    cfg_path = default_cfg_path.resolve()
    if args.config:
        cfg_path = Path(args.config).resolve()

    print(f"Scenario config file used = \"{cfg_path}\"")

    cfg_landcover, cfg_opt = read_from_yaml(cfg_path)

    # Perform this step only of the 'land_cover' section is present in the YAML
    if cfg_landcover is not None:
        perform_land_cover(
            paths=cfg_landcover.paths,
            out_shp=cfg_landcover.out_shp,
            r=cfg_landcover.r,
            class_artificial_indices=cfg_landcover.class_artificial_indices,
        )

    # Perform this step only of the 'optimization' section is present in the YAML
    if cfg_opt is not None:
        perform_optimization(
            paths=cfg_opt.paths,
            et_params=cfg_opt.et_params,
            solver_params=cfg_opt.solver_params,
            num_rows_cost_params=cfg_opt.num_rows_cost_params,
            other_params=cfg_opt.other_params,
        )
