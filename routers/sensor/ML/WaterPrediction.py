import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler
import math


class WaterPrediction:
    df = pd.read_csv("routers/sensor/ML/Result.csv")
    Lin = LinearRegression()
    sc = StandardScaler()
    X = df.iloc[:, :-1].values
    Y = df.iloc[:, -1].values
    new_X = df.iloc[:, [0, 2]].values
    X_train, X_test, Y_train, Y_test = train_test_split(new_X, Y, test_size=0.25, random_state=0)
    X_train = sc.fit_transform(X_train)
    X_test = sc.fit_transform(X_test)
    Lin.fit(X_train, Y_train)
    Y_test_pred = Lin.predict(X_test)

    def getError(self):
        print("R square : ", r2_score(self.Y_test, self.Y_test_pred))
        print("Mean Absolute Error : ", mae(self.Y_test, self.Y_test_pred))
        meanSquareError = mse(self.Y_test, self.Y_test_pred)
        print("Mean Squared Error : ", meanSquareError)
        print("Root Mean Square Error : ", math.sqrt(meanSquareError))

    def predict(self, solarRadiation, maxTemperature):
        waterRequirement = self.Lin.predict(self.sc.fit_transform([[solarRadiation, maxTemperature]]))
        return round(waterRequirement[0], 0)
