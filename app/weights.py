import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import numpy as np
import datetime
from sys import argv
from scipy.optimize import minimize
from operator import itemgetter, attrgetter
TOLERANCE = 1e-10


def _allocation_risk(weights, covariances):
    portfolio_risk = np.sqrt((weights * covariances * weights.T))[0, 0]
    return portfolio_risk


def _assets_risk_contribution_to_allocation_risk(weights, covariances):
    portfolio_risk = _allocation_risk(weights, covariances)
    assets_risk_contribution = np.multiply(weights.T, covariances * weights.T) \
        / portfolio_risk
    return assets_risk_contribution


def _risk_budget_objective_error(weights, args):
    covariances = args[0]
    assets_risk_budget = args[1]
    weights = np.matrix(weights)
    portfolio_risk = _allocation_risk(weights, covariances)
    assets_risk_contribution = \
        _assets_risk_contribution_to_allocation_risk(weights, covariances)
    assets_risk_target = \
        np.asmatrix(np.multiply(portfolio_risk, assets_risk_budget))
    error = \
        sum(np.square(assets_risk_contribution - assets_risk_target.T))[0, 0]
    return error


def _get_risk_parity_weights(covariances, assets_risk_budget, initial_weights):
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
                   {'type': 'ineq', 'fun': lambda x: x})
    optimize_result = minimize(fun=_risk_budget_objective_error,
                               x0=initial_weights,
                               args=[covariances, assets_risk_budget],
                               method='SLSQP',
                               constraints=constraints,
                               tol=TOLERANCE,
                               options={'disp': False})
    weights = optimize_result.x
    return weights


def get_weights(yahoo_tickers=['SPY', 'TLT']):
    tickers = yahoo_tickers
    _start_date = datetime.datetime.now() - datetime.timedelta(days=180)
    _end_date = datetime.datetime.now()
    start_date = _start_date.strftime("%Y-%m-%d")
    end_date = _end_date.strftime("%Y-%m-%d")
    data = yf.download(tickers, start=start_date, end=end_date)
    prices = pd.DataFrame(data["Adj Close"])
    covariances = 52.0 * \
        prices.asfreq('W-FRI').pct_change().iloc[1:, :].cov().values
    assets_risk_budget = [1 / prices.shape[1]] * prices.shape[1]
    init_weights = [1 / prices.shape[1]] * prices.shape[1]
    weights = \
        _get_risk_parity_weights(covariances, assets_risk_budget, init_weights)
    weights = pd.Series(weights, index=prices.columns, name='weight')
    return weights

if __name__ == '__main__':
    try:
        t = argv[1].split(",")
    except:
        print("Must specify list of tickers as comma-separated string e.g. SPY,TLT,BTC-USD")
    sd = datetime.datetime.now() - datetime.timedelta(days=30)
    ed = datetime.datetime.now()
    weights = get_weights(yahoo_tickers=t)
    sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    for i in sorted_weights:
        print("\"{name}\": {val:.2f},".format(name=i[0], val=i[1]))