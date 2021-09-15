# -*- coding: utf-8 -*-
"""Backorder_final_pipeline.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_66hzJsAqi_fVCZ413Pd7nvDVnXmMTFv
"""

## import libraries
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.preprocessing import normalize
import seaborn as sb
from scipy import stats
import numpy as np
from sklearn.preprocessing import normalize, StandardScaler,MinMaxScaler
import joblib
from prettytable import PrettyTable
from tqdm import tqdm 
import math, time
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model, tree, ensemble
import time
from prettytable import PrettyTable
from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, make_scorer, f1_score, recall_score, precision_score, confusion_matrix, roc_curve, precision_recall_curve
from numpy import argmax
import warnings
warnings.filterwarnings("ignore")

#Importing compressed dataset
#!wget https://raw.githubusercontent.com/rodrigosantis1/backorder_prediction/master/dataset.rar

#Extracting the dataset
#!unrar x '/content/dataset.rar'

#df_test = pd.read_csv('Kaggle_Test_Dataset_v2.csv')

#Assigning the numerical columns
num_col_list=['national_inv','lead_time','in_transit_qty','forecast_3_month','forecast_6_month','forecast_9_month','sales_1_month','sales_3_month','sales_6_month','sales_9_month','min_bank','pieces_past_due','perf_6_month_avg','perf_12_month_avg','local_bo_qty']

def final_fun_1(df, return_actual=False):
  
  df_test=df.copy()
  
  #Fetching the best features
  best_feat=joblib.load('test_best_feat.pkl')
  best_feat=best_feat.tolist()
  
  #Fetching the trained standardization object instance
  sc=joblib.load('sc.pkl')
  df_test=df_test[df_test['went_on_backorder'].notna()]

  # Encode categorical columns with values Yes and No to 1 and 0 respectively
  dict_map_bool={'Yes':1.0,'No':0.0}

  df_test['deck_risk']=df_test['deck_risk'].map(dict_map_bool)
  df_test['potential_issue']=df_test['potential_issue'].map(dict_map_bool)
  df_test['oe_constraint']=df_test['oe_constraint'].map(dict_map_bool)
  df_test['ppap_risk']=df_test['ppap_risk'].map(dict_map_bool)
  df_test['stop_auto_buy']=df_test['stop_auto_buy'].map(dict_map_bool)
  df_test['rev_stop']=df_test['rev_stop'].map(dict_map_bool)
  df_test['went_on_backorder']=df_test['went_on_backorder'].map(dict_map_bool)

  #Replacing -99 in perfomance columns with nan
  df_test.perf_6_month_avg.replace({-99.0 : np.nan}, inplace = True)
  df_test.perf_12_month_avg.replace({-99.0 : np.nan}, inplace = True)
  df_test=df_test.drop(columns=['sku'])
  
  #Handling missing values with median values
  df_test.lead_time.replace(to_replace = np.nan, value=8, inplace=True)
  df_test.perf_6_month_avg.replace(to_replace = -99, value=.85, inplace=True)
  df_test.perf_12_month_avg.replace(to_replace = -99, value=.83, inplace=True)

  #Performing Standardization
  df_test_num_sc = sc.transform(df_test[num_col_list].values)
  df_test_num_sc=pd.DataFrame(df_test_num_sc,index=df_test.index,columns=num_col_list)

  #Assigning numerical columns to original dataframe
  for i in num_col_list:
    df_test[i]=df_test_num_sc[i]

  #Function to perform addition of features  
  def add(df,num_cols):
    for i in num_cols:
      for j in num_cols:
        if (i!=j):
          df[i+'_'+j+'_add']=df[i]+df[j]
    return df

  #Function to perform multiplication of features
  def mult(df,num_cols):
    for i in num_cols:
      for j in num_cols:
        if (i!=j):
          df[i+'_'+j+'_mult']=df[i]*df[j]
    return df

  #Function to perform inverse of features
  def inv(df,num_cols):
    for i in num_cols:
      df[i+'_'+'inv']=1/(df[i]+0.001)
    return df

  #Function to perform square of features
  def square(df,num_cols):
    for i in num_cols:
      df[i+'_'+'square']=df[i] * df[i]
    return df

  #Function to perform square root of features
  def sqrt(df,num_cols):
    for i in num_cols:
      df[i+'_'+'square_root']=np.sqrt(abs(df[i]))
    return df

  #Function to perform log of features
  def log(df,num_cols):
    for i in num_cols:
      df[i+'_'+'log']= (np.log(abs(df[i])+1))
    return df


  #Applying tranformed functions
  df_test_trans=add(df_test,num_col_list)
  df_test_trans=mult(df_test_trans,num_col_list)
  df_test_trans=inv(df_test_trans,num_col_list)
  df_test_trans=square(df_test_trans,num_col_list)
  df_test_trans=sqrt(df_test_trans,num_col_list)
  df_test_trans=log(df_test_trans,num_col_list)

  df_test_final = df_test_trans[best_feat]
  y_test=df_test_trans['went_on_backorder'].values

  filename = 'backorder_best_model.pkl'
  model=joblib.load(filename)
  y_pred_test = model.predict(df_test_final)

  return y_test,y_pred_test

def final_fun_2(df):
  
  y_test, y_pred = final_fun_1(df)
  return (y_test,y_pred)

#final_fun_2(df_test)