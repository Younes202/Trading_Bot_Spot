import pandas as pd
import numpy as np
from arch import arch_model
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime, timedelta, timezone
from loguru import logger
import glob
from app.config import settings
import joblib
from app.strategies.indicators import get_opportunity  # Assuming your strategy file is named utils.py
import os


class VolatilityPredictor:
    def __init__(self, data: pd.DataFrame, scale_factor=1000):
        self.data = data
        self.returns = None
        self.model_fitted = None
        self.scale_factor = scale_factor
        logger.info("VolatilityPredictor initialized.")

    def wrangle_data(self):
        logger.info("Starting data wrangling.")
        self.data['log_return'] = np.log(self.data['close_price']).diff().dropna()
        self.returns = (self.data['log_return'] * self.scale_factor).dropna()
        self.data['realized_volatility'] = self.data['log_return'].rolling(window=1).std()

    def fit_egarch_model(self, symbol, p=1, q=1):
        logger.info("Fitting EGARCH model.")
        if self.returns is None:
            raise ValueError("Data must be wrangled before fitting the model.")
        model = arch_model(self.returns, vol='EGARCH', p=p, q=q)
        self.model_fitted = model.fit(disp='off')
        logger.info("EGARCH model fitted.")
        self.dump(symbol)

    def validate_time_input(self, time_input: datetime):
        if time_input.second != 0:
            raise ValueError("Invalid time input: seconds must be 0.")
        return time_input

    def predict_volatility_and_close_price(self, horizon: int):
        logger.info(f"Predicting volatility and close prices for a horizon of {horizon} minutes.")

        model_directory = settings.trained_models  
        model_files = glob.glob(os.path.join(model_directory, "*.pkl"))
        
        if model_files:
            latest_model = max(model_files, key=os.path.getctime)
            logger.info(f"Loading the latest trained model: {latest_model}")
            self.model_fitted = joblib.load(latest_model)
        else:
            logger.info("No model found, fitting a new model.")
            self.fit_egarch_model()

        if self.model_fitted is None:
            raise ValueError("Model must be fitted before predicting volatility.")

        predicted_vols = []
        predicted_close_prices = []
        predicted_open_times = []
        predicted_close_times = []
        last_close_time = self.data["close_time"].iloc[-1]
        user_specified_time = last_close_time.replace(microsecond=0) + timedelta(seconds=1)
        if user_specified_time:
            current_time = self.validate_time_input(user_specified_time).replace(tzinfo=timezone.utc)
        else:
            current_time = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)

        last_close_price = self.data['close_price'].iloc[-1]
        adjustment_factor = 0.5

        for i in range(horizon):
            forecast = self.model_fitted.forecast(horizon=1)
            volatility = np.sqrt(forecast.variance.values[-1, 0])
            predicted_vols.append(volatility)

            predicted_close_price = last_close_price + (volatility * adjustment_factor)
            predicted_close_prices.append(predicted_close_price)

            last_close_price = predicted_close_price
            next_return = np.random.normal(0, volatility)
            self.returns = pd.concat([self.returns, pd.Series([next_return], index=[self.returns.index[-1] + 1])])
            open_time = (current_time + timedelta(minutes=i)).replace(second=0, microsecond=0)
            close_time = (current_time + timedelta(minutes=i)).replace(second=59, microsecond=0)

            predicted_open_times.append(open_time)
            predicted_close_times.append(close_time)

            self.fit_egarch_model()

        predicted_vols = np.array(predicted_vols) / self.scale_factor
        logger.info("Volatility and close price prediction completed.")

        prediction_df = pd.DataFrame({
            'predicted_volatility': predicted_vols,
            'close_price': predicted_close_prices,
            'open_time': predicted_open_times,
            'close_time': predicted_close_times
        })

        print("\n returns : ", self.returns, "\n")
        print("\n data : ", self.data.head(5), "\n")
        print("\n predicted data : ", prediction_df, "\n")
        self.predicted_df = prediction_df

        return self.predicted_df

    def evaluate_model(self, actual_volatility: pd.Series, predicted_volatility: pd.Series):
        logger.info("Evaluating model performance.")
        mse = mean_squared_error(actual_volatility, predicted_volatility)
        mae = mean_absolute_error(actual_volatility, predicted_volatility)
        metrics = {'MSE': mse, 'MAE': mae}
        logger.info(f"Model evaluation metrics: MSE={mse}, MAE={mae}")
        return metrics
    
    def dump(self, symbol):
        # Create timestamp in the desired format using hyphens and underscores for clarity
        current_time = datetime.now().strftime("%d-%m-%Y-%H-%M")
        
        # Create filepath with the symbol and timestamp
        filepath = os.path.join(settings.volatility_trained_models, f"{current_time}-{symbol}-eg.pkl")
        
        # Save the model
        joblib.dump(self.model_fitted, filepath)
        logger.info(f"EGARCH model saved at {filepath}")


    def run(self, horizon: int):
        logger.info(f"Running full pipeline with horizon={horizon} minutes.")
        
        self.wrangle_data()
        self.fit_egarch_model()
        
        self.predicted_df = self.predict_volatility_and_close_price(horizon)

        combined_df = pd.concat([self.data, self.predicted_df], axis=0)

        strategy_name = "rsi_bb_volume"
        data_strategy = get_opportunity(combined_df, strategy_name)
        return data_strategy
