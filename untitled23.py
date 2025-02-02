# -*- coding: utf-8 -*-
"""Untitled23.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1VVdODsKGNW0IxIYdiy_hhOrbXnS_wwDK
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df=pd.read_csv('/content/recruitmentdataset-2022-1.3.csv')

df.head()

df.info()

df.describe()

# Plot Gender Distribution
sns.countplot(x="gender", hue="decision", data=df)
plt.title("Hiring Decision by Gender")
plt.show()

"""# 3️⃣ Bias Detection (Statistical Tests)

## Gender Bias (Chi-square Test)
"""

from scipy.stats import chi2_contingency

# Gender Bias Test
gender_table = pd.crosstab(df["gender"], df["decision"])
chi2, p, dof, expected = chi2_contingency(gender_table)

print(f"Chi-square Statistic: {chi2}")
print(f"P-value: {p}")

if p < 0.05:
    print("⚠️ Gender Bias Detected!")
else:
    print("✅ No Significant Gender Bias Found.")

"""## Age Bias (T-Test)"""

from scipy.stats import ttest_ind

hired_ages = df[df["decision"] == True]["age"]
rejected_ages = df[df["decision"] == False]["age"]

t_stat, p_value = ttest_ind(hired_ages, rejected_ages)

print(f"T-test Statistic: {t_stat}, P-value: {p_value}")

if p_value < 0.05:
    print("⚠️ Age Bias Detected!")
else:
    print("✅ No Significant Age Bias Found.")

"""## Nationality Bias (Disparate Impact)"""

df["decision_numeric"] = df["decision"].astype(int)
nationality_hiring_rates = df.groupby("nationality")["decision_numeric"].mean()

print("Hiring Rate by Nationality:")
print(nationality_hiring_rates)

# Disparate Impact Ratio (Between highest and lowest hiring nationality)
max_hiring = nationality_hiring_rates.max()
min_hiring = nationality_hiring_rates.min()
disparate_impact = min_hiring / max_hiring

print(f"Disparate Impact Ratio: {disparate_impact}")

if disparate_impact < 0.8:
    print("⚠️ Nationality Bias Detected (Disparate Impact < 0.8)")
else:
    print("✅ No Major Nationality Bias Found.")

"""# 4️⃣ Machine Learning Model for Hiring Prediction

## Prepare Features & Target Variable
"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Encode categorical variables
for col in ["gender", "nationality", "ind-degree","sport"]:
    df[col] = LabelEncoder().fit_transform(df[col])

# Select Features & Target Variable
X = df.drop(columns=["Id", "decision", "company", "decision_numeric"])
y = df["decision"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""## Train a Fairness-Aware Model"""

!pip install fairlearn

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference

# Train Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate Model
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(classification_report(y_test, y_pred))

# Fairness Metrics
print(f"Demographic Parity Difference: {demographic_parity_difference(y_test, y_pred, sensitive_features=X_test['gender'])}")
print(f"Equalized Odds Difference: {equalized_odds_difference(y_test, y_pred, sensitive_features=X_test['gender'])}")

from imblearn.over_sampling import SMOTE

# Apply SMOTE to balance the classes
smote = SMOTE(sampling_strategy='auto', random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# Train Model on Balanced Data
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_balanced, y_train_balanced)
y_pred_balanced = model.predict(X_test)

# Evaluate Again
print(f"Accuracy after balancing: {accuracy_score(y_test, y_pred_balanced)}")
print(classification_report(y_test, y_pred_balanced))

from sklearn.model_selection import GridSearchCV

# Define Hyperparameter Grid
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 20],
    'min_samples_split': [2, 5, 10]
}

# Run Grid Search
grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Best Parameters
print(f"Best Params: {grid_search.best_params_}")

# Train Best Model
best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)
y_pred_best = best_model.predict(X_test)

# Evaluate Best Model
print(f"Accuracy: {accuracy_score(y_test, y_pred_best)}")
print(classification_report(y_test, y_pred_best))

from fairlearn.reductions import GridSearch, DemographicParity
from fairlearn.metrics import demographic_parity_difference

# Define Fairness Constraints
constraint = DemographicParity()

# Train Fairness-Aware Model
fair_model = GridSearch(RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=2, random_state=42), constraints=constraint)
fair_model.fit(X_train, y_train, sensitive_features=X_train["gender"])

# Predict and Evaluate Fair Model
y_pred_fair = fair_model.predict(X_test)

print(f"Demographic Parity Difference (Fair Model): {demographic_parity_difference(y_test, y_pred_fair, sensitive_features=X_test['gender'])}")

