# -*- coding: utf-8 -*-
"""predict_price.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WDdhcZXj3hzORKAEz9ea8pQXW_dh3IUk
"""

import pathlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras import metrics
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import Dense

ACTIVATION_1 = 'relu'
ACTIVATION_2 = 'sigmoid'
ACTIVATION_3 = 'sigmoid'

EPOCHS = 10

LEARNING_RATE=0.001

METRICS=   ['mae', 'mse']

NEURON_LAYER_1 =  32
NEURON_LAYER_2 =  32
NEURON_LAYER_3 = 32

PERCENT_TRAINNING = 0.60

CSV_COLUMNS = ["stock_item_id","sales_price","sales_quantity",
               "diference_price","sales_tax_rate","sales_tax_amount",
               "last_cost_Price","quantity_per_Outer","tax_rate",
               "recommended_retail_price"]

raw_dataset = pd.read_csv('exported_data.csv', names=CSV_COLUMNS ,
                      na_values = "?", comment='\t',
                      sep=";", skipinitialspace=True,encoding = 'ISO-8859-1')

dataset = raw_dataset.copy()


dataset = dataset.dropna()
dataset.describe()

train_dataset = dataset.sample(frac=PERCENT_TRAINNING,random_state=0)
test_dataset = dataset.drop(train_dataset.index)
test_dataset_copy = test_dataset

train_stats = train_dataset.describe()
train_stats.pop("sales_price")
train_stats = train_stats.transpose()
train_stats

train_labels = train_dataset.pop('sales_price')
test_labels = test_dataset.pop('sales_price')
stockItemIdArray = test_dataset.get('stock_item_id')
train_dataset.head(10)

def norm(x):
  return (x - train_stats['mean']) / train_stats['std']
normed_train_data = norm(train_dataset)
normed_test_data = norm(test_dataset)

def build_model():
  
  layersArray= [
    layers.Dense(NEURON_LAYER_1, activation=ACTIVATION_1, 
                 input_shape=[len(train_dataset.keys())]),
    layers.Dense(NEURON_LAYER_2, activation=ACTIVATION_2),
  ]

  if NEURON_LAYER_3>0:
    layersArray.append(layers.Dense(NEURON_LAYER_3, activation=ACTIVATION_3)) 

  layersArray.append(layers.Dense(1))

  model = keras.Sequential(layersArray)

  OPTIMIZER= tf.keras.optimizers.Adam(LEARNING_RATE) 
  #OPTIMIZER= tf.keras.optimizers.RMSprop(LEARNING_RATE)
  
  model.compile(loss=METRICS[1],optimizer=OPTIMIZER,metrics=METRICS)
  
  return model

model = build_model()
model.summary()

example_batch = normed_train_data[:10]
example_result = model.predict(example_batch)
example_result

class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('Inicio')
    print('-',epoch, end='')

history = model.fit(
  normed_train_data, train_labels,
  epochs=EPOCHS, validation_split = 0.2, verbose=0,callbacks=[PrintDot()])

hist = pd.DataFrame(history.history)
hist['epoch'] = history.epoch
hist.tail()

def plot_history(history):
  hist = pd.DataFrame(history.history)
  hist['epoch'] = history.epoch

  if 'mae' in hist:
    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Abs Error [salesPrice]')
    plt.plot(hist['epoch'], hist['mae'],
           label='Train Error')
    plt.plot(hist['epoch'], hist['val_mae'],
           label = 'Val Error')
    plt.ylim([0,5])
    plt.legend()
  
  if 'mse' in hist:
    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Square Error [$sales_price^2$]')
    plt.plot(hist['epoch'], hist['mse'],
           label='Train Error')
    plt.plot(hist['epoch'], hist['val_mse'],
           label = 'Val Error')
    plt.ylim([0,20])
    plt.legend()


  plt.show()


  
plot_history(history)

test_predictions = model.predict(normed_test_data).flatten()

plt.scatter(test_labels, test_predictions)
plt.xlabel('True Values [salesPrice]')
plt.ylabel('Predictions [salesPrice]')
plt.axis('equal')
plt.axis('square')
plt.xlim([0,plt.xlim()[1]])
plt.ylim([0,plt.ylim()[1]])
_ = plt.plot([-100, 2000], [-100, 2000])

error = test_predictions - test_labels
plt.hist(error, bins = 25)
plt.xlabel("Prediction Error [salesPrice]")
_ = plt.ylabel("Count")

loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)

print("Testing set Mean Abs Error: {:5.2f} sales_price".format(mae))

error = test_predictions - test_labels
plt.hist(error, bins = 25)
plt.xlabel("Prediction Error [sales_price]")
_ = plt.ylabel("Count")

for stockItemId,originalValue,prediction in zip(stockItemIdArray,test_labels,test_predictions):
  print("stock_item_id:",stockItemId,"Original Value:",originalValue,"prediction Value:",prediction)
