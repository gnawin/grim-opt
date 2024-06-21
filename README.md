## Installation steps

* OPTIONAL, only if plotting is necessary:
  + Install the `libgeos` library and development headers
  + In Ubuntu: `sudo apt install libgeos-dev`

* Use `pip` to install the `grim-opt` library and executable normally.
  + Recommended: do it in a fresh virtual environment
    - Create env: `python3 -m venv <chosen_venv_directory>`
    - Activate env: `source <chosen_venv_directory>/bin/activate`

* TBD: Conda environment file (handles geos dependency also)

## Instructions for contributing to the project

### One-time setup

* This project uses `poetry` as its dependency management, virtualenv management and release (build) tool
   + Install following the steps described in https://python-poetry.org/docs/#installation

* Setup PyPI credentials to be able to publish packages
   1. Make an account on `https://pypi.org`. Ask (optional) for invitation to become project contributor on PyPI.
   2. Add API token on the "account settings" page of PyPI (global scope)
   3. Register the API token to be the one used by Poetry: `poetry config pypi-token.pypi "<your_api_token>"`

### Sometimes: update package dependencies

* It is advisable to sometimes (every couple of months) update the package's dependencies
  + Using newer versions (if possible) of dependencies gives you above all security fixes
    - Sometimes also performance improvements

* Steps:
  1. First make a backup of the lock file (in case you need to rollback the update):
    - `mv poetry.lock bkp-poetry.lock`
  2. Then create a new lock file with updated versions of dependencies, and install all fresh:
    - `poetry update --lock`
    - `poetry env remove python && poetry install`
  3. Test that the program still works as expected
  4. If the program breaks after the update, revert to the previous state by restoring the old lock file:
    - `mv bkp-poetry.lock poetry.lock`
    - `poetry env remove python && poetry install`

### Building a new version and releasing/uploading to PyPI

* Building a (new) release and publishing it to PyPI:
   1. Do the actual contribution to the project 🙂
   2. Increment the package's version number in `pyproject.toml`
   3. Build the package (wheel and source): `poetry build`. The built artifacts will be placed in the `dist` folder
   4. Publish to PyPI: `poetry publish`


### Contributing to documentation and build the docs

TODO


## Processing steps

### Area per land cover per region 
* Module/function name: `land_cover.py`
* Input data:
  + `corine_land_cover`
  + `polygons`
* Outputs:
  + `region_area_land_cover_classes`

* From `region_area_land_cover_classes`, we aggregate (manually) into: `region_area_generation`

### Optimize investment
* Module/function name: `optimization.py`
* Input data
  + `region_area_generation`
  + `electricity_demand`
  + `electricity_gencap_factors_new_solar`
  + `electricity_gencap_factors_new_wind`
  + `electricity_gencap_existing`
  + `electricity_transcap_connections`
* Input parameters:
  + Techno-economic: `parameters_techno_econ.xlsx`
* Outputs (`{pct}` is the proportion of the overall generation capacity required to be renewable):
  + One file for each value of `{pct}`: 0%, 20%, 50%, 80%, 100%
    - `optimized_gencap_{pct}_renew`
    - `optimized_transcap_{pct}_renew`

### Post-processing / plotting
* Module/function name:
  + `plot_capacities_totals.py`
* Input data:
  + One file for each value of `{pct}`: 0%, 20%, 50%, 80%, 100%
    - `optimized_gencap_{pct}_renew`
    - `optimized_transcap_{pct}_renew`
* Output:
  + `plot_capacities_totals`

* Module/function name:
  + `plot_capacities_regions.py`
* Input data:
  + One file for each value of `{pct}`: 0%, 20%, 50%, 80%, 100%
    - `optimized_transcap_{pct}_renew`
* Output:
  + `plot_capacities_regions`


## File meaning, format and data description

### `corine_land_cover`
* netcdf file: Corine land cover data
* out_shp: the size of the Corine land cover data. For example, (4721, 4412) means 4721 points in y dimension and 4412 points in x dimension.
* r: radius of circles where the circle area will be excluded from the available points/land cover. It should be used in combination with "class_artificial_indices".
* class_artificial_indices: a list contains grid codes from Corine land cover data which present centers of the cirlces. The grid codes could be found in file "clc_legend_new.xls". The default values are artificial surfaces. Detailed description of the Corine land cover classes could be found in: https://land.copernicus.eu/user-corner/technical-library/corine-land-cover-nomenclature-guidelines/html. 
* EPSG3035/EPSG4326 are parameters for EPSG coordinate systems. For example, the EPSG 3035 system is constructed as: EPSG3035 = pyproj.Proj("+init=EPSG:3035").  

### `polygons`
* geojson files: polygon data (in my case, I created the polygon data myself) 

### Optimization inputs
* `electricity_demand`
  + Demand data (for countries: can be obtained from `ENTSO-E`, but need to be cleaned). The data is in MWh, per node, per time step.
* Wind and solar data
  + Can be obtained from `renewable.ninja`, but need to be cleaned
  + `electricity_gencap_factors_new_solar`.  The data is unitless between 0 - 1, per node, per time step.
  + `electricity_gencap_factors_new_wind`.  The data is unitless between 0 - 1, per node, per time step.

* `electricity_gencap_existing`
  + existing generation data. The data is in MW, per node, per technology.
* `electricity_transcap_connections`
  + line data (transmission capacities of inter-region connections). The data shows the details of the lines. In my case, both ends of the lines are represented by region numbers. The regions numbers can be found in file "region_numbered.csv" 
* `techno_economic_parameters.xlsx`
  + techno-economic data

### `region_area_land_cover_classes`
* csv file (matrix): for each land cover class, for each region, the area (m2). 

### `region_area_generation`
* Some manual calculations are done, for summation and suitability factors.
  + Per column, the area in km2

### `optimization`
* sets
  + N: number of nodes. 
  + FL: number of lines.
  + G: all generation technologies.
  + SC: storage conversion. S = SC
  + S: storage technologies. S = SC
  + RES: renewable energy technologies. Subset of G
  + VRES: variable renewable energy technologies. Subset of RES.
  + Non-VRES: non-variable renewable energy technologies. G-VRES.
  + T = time steps
  + T2 =time steps excluding the first time step  
* parameters.
  + capacity_density_onshore: capacity density for onshore wind turbines (MW/km2)
  + capacity_density_solar: capacity density for solar PV (MW/km2)
  + lol: value of lost load (euros/MWh)
  + R: number of time steps. Used in combination with T, T2. 
  + CT: cost transmission line (euros/km/MW)
  + r: discount rate (0 - 1)
  + LT: lifetime transmission line
  + reserve_margin: reserve capacity in percentage (0 - 1), i.e., extra capacity to be built but will now be used.
  + omega: renewable energy target, 0 - 1.
  + im = np.zeros([len(df.index), 32]): 32 is number of nodes
  + arr_demand = np.empty([32, 8760]): 32 is number of nodes, 8760 is number of time steps (in my case, hours). Same for other arrays.
  + e_l: percentage of extra length of the lines (0 - 1), accounting for routing due to non-straight lines.
* solver options
  + solver_name: name of the solver
  + solver_crossover: crossover. Default is 0 (disabled) 
  + solver_method: method to solve the problem. Default is 2 (barrier method)
  + solver_threads: number of threads to use. 
  
### Optimized capacities
* `optimized_gencap_{pct}_renew`
  + MW, per technology, per node
* `optimized_transcap_{pct}_renew`
  + MW, between nodes
  
### Plots
* `plots_capacities_totals`
  + For each scenario (pct. of renewables in generation mix), for each energy source the installed capacity

* `plots_capacities_regions`
  + For each scenario (pcr. of renewables in generation mix), for each energy source, for each region the installed capacity


 
