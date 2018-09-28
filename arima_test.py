import warnings
import itertools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
from prediction import Model
from arima import Arima

plt.style.use('fivethirtyeight')

def find_best():
    data1 = pd.read_csv("band.csv", index_col=0)

    # reduce dataset
    # data1 = data1[:800]

    # Interpret index as timestamp
    data1.index = pd.to_datetime(data1.index)

    forecast = None

    for count in range(0, len(data1)-150, 15):
        training_data = data1[count:count+150]
        model = Model(training_data, True)
        model.fit()
        if count == 0:
            forecast = model.predict(15, 1)
        else:
            forecast = forecast.append(model.predict(15, 1))

    # save on file the predicted values
    forecast.to_csv('pred-best.csv', sep=',')

    ax = data1.plot(label='observed', figsize=(20, 15))
    forecast.plot(ax=ax, label='Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel('Bandwidth [B/s]')

    plt.legend()
    plt.show()


def find_best_no_seasonal():
    data1 = pd.read_csv("band.csv", index_col=0)

    # reduce dataset
    # data1 = data1[:800]

    # Interpret index as timestamp
    data1.index = pd.to_datetime(data1.index)

    forecast = None

    for count in range(0, len(data1)-150, 15):
        training_data = data1[count:count+150]
        model = Model(training_data, True)
        model.fit_no_seasonal()
        if count == 0:
            forecast = model.predict_no_seasonal(15, 1)
        else:
            forecast = forecast.append(model.predict_no_seasonal(15, 1))

    # save on file the predicted values
    forecast.to_csv('pred-best-no-s.csv', sep=',')

    ax = data1.plot(label='observed', figsize=(20, 15))
    forecast.plot(ax=ax, label='Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel('Bandwidth [B/s]')

    plt.legend()
    plt.show()

def garch():
    data1 = pd.read_csv("band.csv", index_col=0)

    # reduce dataset
    # data1 = data1[:800]

    # Interpret index as timestamp
    data1.index = pd.to_datetime(data1.index)

    forecast = None

    for count in range(0, len(data1) - 150):
        print(count)
        training_data = data1[count:count + 150]
        model = Arima(training_data)
        model.fit_with_garch(150)
        if count == 0:
            forecast = model.predict_with_garch(1)
        else:
            forecast = forecast.append(model.predict_with_garch(1))

    # save on file the predicted values
    forecast.to_csv('pred-best-garch.csv', sep=',')
    print(forecast.head())

    ax = data1.plot(label='observed', figsize=(20, 15))
    forecast.plot(ax=ax, label='Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel('Bandwidth [B/s]')

    plt.legend()
    plt.show()


def holt_winters():
    data1 = pd.read_csv("band.csv", index_col=0)
    data1.index = pd.to_datetime(data1.index)
    pred = None
    warnings.filterwarnings("ignore")  # specify to ignore warning messages

    for count in range(0, len(data1)-150, 15):
        training_data = data1[count:count+150]
        fit1 = ExponentialSmoothing(training_data['BW'], seasonal_periods=7, trend='add', seasonal='add', ).fit()
        if count == 0:
            forecast = fit1.forecast(15)
            future_ts = [v + pd.to_timedelta(1 * (i + 1), unit='s')
                         for i, v in enumerate([training_data.index[-1]] * 15)]
            pred = pd.DataFrame(forecast.values, index=future_ts, columns=['Prediction'])
        else:
            forecast = fit1.forecast(15)
            future_ts = [v + pd.to_timedelta(1 * (i + 1), unit='s')
                         for i, v in enumerate([training_data.index[-1]] * 15)]
            future_forecast = pd.DataFrame(forecast.values, index=future_ts, columns=['Prediction'])
            print(future_forecast)
            pred = pred.append(future_forecast)

    # save on file the predicted values
    pred.to_csv('pred-best-holt.csv', sep=',')
    print(pred.head())

    ax = data1.plot(label='observed', figsize=(20, 15))
    pred.plot(ax=ax, label='Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel('Bandwidth (B/s)')

    plt.legend()
    plt.show()


def compare_50():
    data1 = pd.read_csv("band.csv", index_col=0)
    # Interpret index as timestamp
    data1.index = pd.to_datetime(data1.index)
    data1 = data1[:50]

    data1.plot(figsize=(15, 6))
    plt.show()


    model = Model(data1)


    warnings.filterwarnings("ignore") # specify to ignore warning messages

    mod = sm.tsa.statespace.SARIMAX(data1,
                                    order=(1, 1, 1),
                                    seasonal_order=(1, 1, 1, 12),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

    results = mod.fit(disp=0)

    print(results.summary().tables[1])

    results.plot_diagnostics(figsize=(15, 12))
    plt.show()

    # Get forecast 50 steps ahead in future
    pred_uc = results.get_forecast(steps=50)

    # Get confidence intervals of forecasts
    pred_ci = pred_uc.conf_int()

    future_ts = [v + pd.to_timedelta(1 * (i + 1), unit='s')
                 for i, v in enumerate([data1.index[-1]] * 50)]
    future_forecast = pd.DataFrame(pred_uc.predicted_mean.values, index=future_ts, columns=['Prediction'])
    # future_forecast.plot(label='Forecast')

    ax = data1.plot(label='observed', figsize=(20, 15))
    future_forecast.plot(ax=ax, label='Forecast')

    ax.set_xlabel('Date')
    ax.set_ylabel('CO2 Levels')

    plt.legend()
    plt.show()


# find_best()
# find_best_no_seasonal()
# garch()
holt_winters()

'''pred = results.get_prediction(start=150, dynamic=False)
pred_ci = pred.conf_int()

ax = data1[150:].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7)

ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)

ax.set_xlabel('Date')
ax.set_ylabel('Bandwidth')
plt.legend()
plt.show()

y_forecasted = pred.predicted_mean
y_truth = data1[150:]

# Compute the mean square error
mse = mean_squared_error(y_truth, y_forecasted)
print('The Mean Squared Error of our forecasts is {}'.format(round(mse, 2)))

'''