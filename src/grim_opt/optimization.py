#  Copyright 2021 Technische Universiteit Delft
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import pandas as pd
import numpy as np
from numpy.linalg import inv, multi_dot
from pyomo.environ import NonNegativeReals, Var, ConcreteModel, Objective, Constraint, SolverFactory

from grim_opt.config import OptimizationPaths, EnergyTechParams, SolverParams, OptOtherParams
from grim_opt.config_defaults import config_optimization_default


def perform_optimization(
        paths: OptimizationPaths,
        et_params: EnergyTechParams,
        solver_params: SolverParams,
        num_rows_cost_params: int,
        other_params: OptOtherParams,
        ):
    """
    Perform the optimization step in which the investments for renewable energy generation and transmission are calculated.

    :param paths Struct with all the filepaths (input and output) needed for this processing step
    :type paths OptimizationPaths
    :param et_params:
    :param solver_params:
    :param num_rows_cost_params: Number of rows in the cost parameters spreadsheet
    :param other_params:

    :return:
    """
    # Unpack here to avoid long and verbose variable names from here onwards
    N = et_params.N
    FL = et_params.FL
    G = et_params.G
    SC = et_params.SC
    RES = et_params.RES
    non_VRES = et_params.non_VRES

    lol = other_params.lol
    R = other_params.R
    denominator_R = other_params.denominator_R
    T = other_params.T
    T2 = other_params.T2
    CT = other_params.CT
    r = other_params.r
    LT = other_params.LT
    reserve_margin = other_params.reserve_margin
    omega = other_params.omega
    e_l = other_params.e_l

    S = SC
    # VRES = ['onshore', 'solar']

    # cost parameters
    df_parameters = pd.read_excel(paths.params_techno_econ, index_col=0)
    C = {i: num_rows_cost_params * df_parameters.loc[i, 'CapEx(€/kW)'] for i in (G + SC)}
    C_S = {i: num_rows_cost_params * df_parameters.loc[i, 'CapExStorage(€/kWh)'] for i in S}  # €/MW
    a = {i: num_rows_cost_params * df_parameters.loc[i, 'FOM(€/kW/yr)'] for i in (G + SC)}  # €/MW/yr
    b = {i: num_rows_cost_params * df_parameters.loc[i, 'VOM(€/kWh)'] for i in G}  # €/MWh
    L = {i: df_parameters.loc[i, 'Lifetime(yr)'] for i in (G + SC + S)}
    # e = {i: df_parameters.loc[i, 'Pollution(tCO2/MWh)'] for i in G}  # TODO: is this used? when?
    # eta = {i: df_parameters.loc[i, 'eta'] for i in G}  # TODO: is this used? when?
    eta_in = {i: df_parameters.loc[i, 'eta_in'] for i in SC}
    eta_out = {i: df_parameters.loc[i, 'eta_out'] for i in SC}

    # land-use data
    df_KM = pd.read_csv(paths.region_area_generation, index_col=0)
    KM_onshore = {n: df_KM.loc[n, 'wind'] for n in N}
    KM_solar = {n: df_KM.loc[n, 'solar'] for n in N}
    capacity_density_onshore = 5  # MW/km2
    capacity_density_solar = 30  # MW/km2

    # existing generation capacity
    df_generation = pd.read_excel(paths.gencap_existing)
    existing_capacity = df_generation.fillna(0)

    # create PTDF
    df = pd.read_csv(paths.transcap_connections)
    im = np.zeros([len(df.index), 32])

    for line in df.index:
        im[line, df.loc[line, 'region1']] = 1
        im[line, df.loc[line, 'region2']] = -1

    A = im
    Bd = np.diag([1 / x for x in df['x']])
    M1 = multi_dot([Bd, A])
    M2 = multi_dot([A.transpose(), Bd, A])
    # node 0 is slack node
    PTDF_slack = multi_dot([M1[:, 1:], inv(M2[1:, 1:])])
    PTDF = np.hstack((np.zeros([len(df.index), 1]), PTDF_slack))

    existing_line = df['capacity']
    distance = df['length']

    # time-series data
    df_demand = pd.read_csv(paths.electricity_demand)  # MWh
    df_onshore = pd.read_csv(paths.electricity_gencap_factors_new_wind)
    df_solar = pd.read_csv(paths.electricity_gencap_factors_new_solar)

    arr_demand = np.empty([32, denominator_R])
    arr_onshore = np.empty([32, denominator_R])
    arr_solar = np.empty([32, denominator_R])

    for n in N:
        arr_demand[n, :] = df_demand[str(n)]
        arr_onshore[n, :] = df_onshore[str(n)]
        arr_solar[n, :] = df_solar[str(n)]

    # create optimization model
    model = ConcreteModel()

    # declare variables
    model.K = Var((G + SC), N, domain=NonNegativeReals)
    model.K_S = Var(S, N, domain=NonNegativeReals)
    model.P = Var(G, N, T, domain=NonNegativeReals)
    model.lol = Var(N, T, domain=NonNegativeReals)
    model.DP = Var(SC, N, T, domain=NonNegativeReals)
    model.CP = Var(SC, N, T, domain=NonNegativeReals)
    model.SP = Var(S, N, T, domain=NonNegativeReals)
    model.K_T = Var(FL, domain=NonNegativeReals)  # FL is flow connections, in terms of numbers
    model.F = Var(FL, T)
    model.Z_net = Var(N, T)

    # objective components
    cost_investment_generationAndConversion = \
        R / denominator_R \
        * (sum(C[i] * (1 + reserve_margin) * model.K[i, n] / ((1 - 1 / (1 + r) ** L[i]) / r) for i in (G + SC) for n in N))

    cost_investment_storage = \
        R / denominator_R \
        * (sum(C_S[i] * (1 + reserve_margin) * model.K_S[i, n] / ((1 - 1 / (1 + r) ** L[i]) / r) for i in S for n in N))

    cost_investment_transmission = \
        R / denominator_R \
        * (sum(distance[i] * e_l * CT * model.K_T[i] / ((1 - 1 / (1 + r) ** LT) / r) for i in FL))  # 25% extra length

    cost_operation = \
        R / denominator_R \
        * (sum((existing_capacity.loc[n, i] + (1 + reserve_margin) * model.K[i, n]) * a[i] for i in (G + SC) for n in N)) \
        + sum(b[i] * model.P[i, n, t] for i in G for n in N for t in T)

    cost_lol = sum(model.lol[n, t] * lol for n in N for t in T)

    # declaring objective function
    model.obj = Objective(
        expr=cost_investment_generationAndConversion +
        cost_investment_storage +
        cost_investment_transmission +
        cost_operation +
        cost_lol
    )

    # constructing constraints
    def node_power_balance_rule(mod, n, t):
        return sum(mod.P[i, n, t] for i in G) + mod.lol[n, t] + \
               sum(mod.DP[i, n, t] - mod.CP[i, n, t] for i in SC) - \
               arr_demand[n, t] == mod.Z_net[n, t]

    def arbitrage_balance_rule(mod, t):
        return sum(mod.Z_net[n, t] for n in N) == 0

    def power_flow_rule(mod, ell, t):
        return mod.F[ell, t] == sum(PTDF[ell, n] * mod.Z_net[n, t] for n in N)

    def transmission_upper_limit_rule(mod, ell, t):
        return mod.F[ell, t] <= mod.K_T[ell] / 2 + existing_line[ell]

    def transmission_lower_limit_rule(mod, ell, t):
        return mod.F[ell, t] >= - (mod.K_T[ell] / 2 + existing_line[ell])

    def max_output_rule1(mod, n, t):
        return mod.P['onshore', n, t] <= arr_onshore[n, t] * (mod.K['onshore', n] + existing_capacity.loc[n, 'onshore'])

    def max_output_rule2(mod, n, t):
        return mod.P['solar', n, t] <= arr_solar[n, t] * (mod.K['solar', n] + existing_capacity.loc[n, 'solar'])

    def max_output_rule3(mod, i, n, t):
        return mod.P[i, n, t] <= mod.K[i, n] + existing_capacity.loc[n, i]

    def storage_rule_start(mod, i, n):
        return mod.SP[i, n, 0] == mod.SP[i, n, T[-1]] \
               + eta_in[i] * mod.CP[i, n, 0] - 1 / eta_out[i] * mod.DP[i, n, 0]

    def storage_rule(mod, i, n, t):
        return mod.SP[i, n, t] == mod.SP[i, n, (t - 1)] \
               + eta_in[i] * mod.CP[i, n, t] - 1 / eta_out[i] * mod.DP[i, n, t]

    def storage_limit(mod, i, n, t):
        return mod.SP[i, n, t] <= mod.K_S[i, n]

    def charging_limit(mod, i, n, t):
        return mod.CP[i, n, t] <= mod.K[i, n]

    def discharging_limit(mod, i, n, t):
        return mod.DP[i, n, t] <= mod.K[i, n]

    def RES_share(mod):
        return omega * sum(mod.P[i, n, t] for i in RES for n in N for t in T) \
               >= sum(mod.P[i, n, t] for i in G for n in N for t in T)

    def max_wind_capacity(mod, n):
        return mod.K['onshore', n] * (1 + reserve_margin) \
               + existing_capacity.loc[n, 'onshore'] <= KM_onshore[n] * capacity_density_onshore

    def max_solar_capacity(mod, n):
        return mod.K['solar', n] * (1 + reserve_margin) \
               + existing_capacity.loc[n, 'solar'] <= KM_solar[n] * capacity_density_solar

    # declaring constraints
    model.node_power_balance = Constraint(N, T, rule=node_power_balance_rule)
    model.arbitrage_balance = Constraint(T, rule=arbitrage_balance_rule)
    model.power_flow = Constraint(FL, T, rule=power_flow_rule)
    model.transmission_upper_limit = Constraint(FL, T, rule=transmission_upper_limit_rule)
    model.transmission_lower_limit = Constraint(FL, T, rule=transmission_lower_limit_rule)
    model.max_output_rule1 = Constraint(N, T, rule=max_output_rule1)
    model.max_output_rule2 = Constraint(N, T, rule=max_output_rule2)
    model.max_output_rule3 = Constraint(non_VRES, N, T, rule=max_output_rule3)
    model.storage_rule_start = Constraint(S, N, rule=storage_rule_start)
    model.storage_rule = Constraint(S, N, T2, rule=storage_rule)
    model.storage_limit_rule = Constraint(S, N, T, rule=storage_limit)
    model.charging_limit_rule = Constraint(SC, N, T, rule=charging_limit)
    model.discharging_limit_rule = Constraint(SC, N, T, rule=discharging_limit)
    model.RES_share_rule = Constraint(rule=RES_share)
    model.max_wind_capacity_rule = Constraint(N, rule=max_wind_capacity)
    model.max_solar_capacity_rule = Constraint(N, rule=max_solar_capacity)
    print('Model building finished!')

    opt = SolverFactory(solver_params.name)

    if solver_params.crossover:
        opt.options["crossover"] = solver_params.crossover

    if solver_params.method:
        opt.options["Method"] = solver_params.method

    if solver_params.threads:
        opt.options["Threads"] = solver_params.threads

    opt.solve(model)
    print('Model solved!')

    # Post-processing
    # save data in dataframes
    def evaluation(indexedvar):
        return pd.Series(indexedvar.get_values())

    # Output:
    # noinspection PyTypeChecker
    evaluation(model.K).unstack().to_csv(paths.optimized_gencap_renew)
    # noinspection PyTypeChecker
    evaluation(model.K_T).to_csv(paths.optimized_transcap_renew)


def default_perform_optimization():
    perform_optimization(
        paths=config_optimization_default.paths,
        et_params=config_optimization_default.et_params,
        solver_params=config_optimization_default.solver_params,
        num_rows_cost_params=config_optimization_default.num_rows_cost_params,
        other_params=config_optimization_default.other_params,
    )


if __name__ == '__main__':
    default_perform_optimization()

