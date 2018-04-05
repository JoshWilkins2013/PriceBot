import sys
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split as tts
from sklearn.cross_validation import KFold
from sklearn.cross_validation import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error

user_model = str(sys.argv[1])
orig_df = pd.read_csv(user_model + '.csv')

#all_cols = ['Title', 'Year', 'Mileage', 'Condition', 'Color', 'Title Status', 'Transmission', 'Size', 'Type', 'Cost', 'Link']

#new_col = 'Size'
cols = ['Year', 'Mileage', 'Type', 'Cost']
#cols.append(new_col)
df = orig_df[cols]
df = df.dropna(axis=0, how='any')

df["Type"] = df["Type"].astype('category')
df["Type"] = df["Type"].cat.codes

#df[new_col] = df[new_col].astype('category')
#df[new_col] = df[new_col].cat.codes

df = df.reset_index(drop=True)

y = df['Cost']
del df['Cost']

X = df
#X = pd.get_dummies(df, columns=["Type"], prefix=["Type"])

#mean_squared_error(y_true, y_pred)

X_train, X_test, y_train, y_test = tts(X, y, test_size=0.3, random_state=4)
logreg = LogisticRegression()
logreg.fit(X_train, y_train)
y_pred = logreg.predict(X_test)
score = 100 - np.mean(np.abs((100 * (y_pred - y_test)/y_test)))
print score

X_train, X_test, y_train, y_test = tts(X, y, test_size=0.3, random_state=4)
knn = KNeighborsClassifier(n_neighbors=2)
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)
score = 100 - np.mean(np.abs((100 * (y_pred - y_test)/y_test)))
print score



# Cross Validation
#knn = KNeighborsClassifier(n_neighbors=5)
#scores = cross_val_score(knn, X, y, cv=10, scoring='neg_mean_squared_error')
#print(np.mean(scores))
