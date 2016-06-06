import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score


##read in the processed Divvy data 
merged_master = pd.read_csv('/Users/mgiangreco/Dropbox/divvy/divvy_rentals.csv')
merged_master.set_index(['index'], drop=True, inplace=True)
merged_master.index = pd.to_datetime(merged_master.index)


#separate dependent from independent variables
X = merged_master.iloc[:, 1:]
y = merged_master['trip_count']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, 
                                                    random_state=1)

#specify random forest regression model
forest = RandomForestRegressor(n_estimators=500, 
                            criterion='mse', max_depth=None, 
                            min_samples_split=2, min_samples_leaf=25, 
                            max_features='auto', max_leaf_nodes=None, 
                            bootstrap=True, oob_score=False, n_jobs= -1, 
                            random_state=None, verbose=2)

#fit the model to the data
forest.fit(X_train, y_train)

#print prediction accuracy
y_train_pred = forest.predict(X_train)
y_test_pred = forest.predict(X_test)

print ('MAE train: %.3f, test: %.3f' % (mean_absolute_error(y_train, y_train_pred), 
                                        mean_absolute_error(y_test, y_test_pred)))
print ('MAE train: %.3f, test: %.3f' % (mean_squared_error(y_train, y_train_pred), 
                                        mean_squared_error(y_test, y_test_pred)))
print ('R^2 train: %.3f test: %.3f' % (r2_score(y_train, y_train_pred), 
                                       r2_score(y_test, y_test_pred)))

#score the model with 5-fold cross-validation 
scores = cross_val_score(estimator=forest, X=X_train, y=y_train, 
                         scoring='mean_absolute_error', cv=5)
print ('CV MAE scores: %s' % scores)
print ('CV MAE: %.3f +/- %.3f' % (np.mean(scores), np.std(scores)))
    

#specify linear regression model
ols = LinearRegression(normalize=True)

#fit the model to the data
ols.fit(X_train, y_train)

#print prediction accuracy
y_train_pred = ols.predict(X_train)
y_test_pred = ols.predict(X_test)

print ('MAE train: %.3f, test: %.3f' % (mean_absolute_error(y_train, y_train_pred), 
                                        mean_absolute_error(y_test, y_test_pred)))
print ('MSE train: %.3f, test: %.3f' % (mean_squared_error(y_train, y_train_pred), 
                                        mean_squared_error(y_test, y_test_pred)))
print ('R^2 train: %.3f test: %.3f' % (r2_score(y_train, y_train_pred), 
                                       r2_score(y_test, y_test_pred)))

#specify gradient boosting machine

params = {'n_estimators': 1000, 'max_depth': 6, 'min_samples_leaf': 25,
          'learning_rate': 0.01, 'loss': 'ls', 'verbose': 1}
clf = ensemble.GradientBoostingRegressor(**params)

clf.fit(X_train, y_train)

#print prediction accuracy
y_train_pred = clf.predict(X_train)
y_test_pred = clf.predict(X_test)

print ('MSE train: %.3f, test: %.3f' % (mean_squared_error(y_train, y_train_pred), 
                                        mean_squared_error(y_test, y_test_pred)))
print ('MAE train: %.3f, test: %.3f' % (mean_absolute_error(y_train, y_train_pred), 
                                        mean_absolute_error(y_test, y_test_pred)))
print ('R^2 train: %.3f test: %.3f' % (r2_score(y_train, y_train_pred), 
                                       r2_score(y_test, y_test_pred)))

