# importing the dataset
import pandas 
import numpy
from sklearn import preprocessing
import numpy as np
from sklearn import pipeline
 
df = pandas.read_csv('./data/data.csv')   

print(df.head())
print(df.shape)
print(df.info())

#lets convert the columns into relevant datatype
category_columns = ["workclass", "marital-status","education", "race", "occupation", "relationship", "gender", "native-country","income"]
numeric_columns =  [ col for col in df.columns if df[col].dtype=='int64' ]

#check for imbalances in dataset
for col in category_columns:
    print(df[col].value_counts())


for col in category_columns:
    df[col]= df[col].astype("category")
    #remove leading and trailing spaces
    df[col] = df[col].str.strip()

category_columns.remove('income')

#there are no null values though there are ? in the dataset. 
# We will comvert all the ? into NAN and then impute values

df[df == '?'] = np.nan


#lets check values in these categorical columns to detect any oulier sample
for col in category_columns:
    print(df[col].value_counts())


#The country Holand-Netherlands  has only one sample. For the purpose of this exercise lets drop this record.
df = df[df['native-country'] != "Holand-Netherlands"]


#lets check which columns have NAN now
print(df.isnull().sum())


#no null values exist so now we can go agead and select feature verctor and target variables
X =  df.drop(['income'], axis=1)
y = df['income'] 


#Splitting data into train and test
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test =  train_test_split(X, y, test_size=.2, random_state=123, stratify=y)

#Feature engineering
# we will encode the categorical variables by using one hot encoder from sklearn preprocessing
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.compose import make_column_selector
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

#this link gave me a good idea of how to use OHE and standard scaler in pipeline model
#https://stackoverflow.com/questions/48673402/how-can-i-standardize-only-numeric-variables-in-an-sklearn-pipeline


#for categorical data processing
categorical_feature_transformer = pipeline.Pipeline(steps = [ ("categorical_imputer", SimpleImputer(strategy='most_frequent')),
        ("OHE", OneHotEncoder(sparse=False, handle_unknown="ignore", drop='first'))])

#numeric featgure processing
numeric_feature_transformer = pipeline.Pipeline(steps = [('numeric_scaler', StandardScaler())])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_feature_transformer, numeric_columns),
        ('cat', categorical_feature_transformer, category_columns)])

#classification

models = {}
from sklearn.linear_model import LogisticRegression

clf = pipeline.Pipeline(steps=[('preprocessor', preprocessor),
                      ('logistic_regression', LogisticRegression())])

models['LogisticRegression'] = clf



#model 2
from sklearn.ensemble import RandomForestClassifier

clf = pipeline.Pipeline(steps=[('preprocessor', preprocessor),
                      ('RandomForestClassifier', RandomForestClassifier())])

models['RandomForestClassifier'] = clf


#model 3
from sklearn.tree import DecisionTreeClassifier

clf = pipeline.Pipeline(steps=[('preprocessor', preprocessor),
                      ('DecisionTreeClassifier', DecisionTreeClassifier())])

models['DecisionTreeClassifier'] = clf


#iterating over all the models 
for model in models:
    models[model].fit(X_train, y_train)
    score = models[model].score(X_test, y_test)
    print(model+'  accuracy score with all the features: {0:0.4f}'. format(score))

# Best model is Random Forest Classifier 
# Before dumping the model out as pkl I will retrain on the entire dataset
clf = pipeline.Pipeline(steps=[('preprocessor', preprocessor),
                      ('RandomForestClassifier', RandomForestClassifier())])

clf.fit(X, y) 


#write model out as pkl
import joblib
joblib.dump(clf, './best_model.pkl')