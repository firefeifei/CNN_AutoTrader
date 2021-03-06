# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 20:26:02 2018

@author: Administrator
"""

import tushare as ts
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import time

def WeightVariable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def BiasVariable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def Conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def MaxPool2x2(x):
    return tf.nn.max_pool(x, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')

#定义CNN
xs = tf.placeholder(tf.float32, [None, 80])
ys = tf.placeholder(tf.float32, [None, 2])
keep_prob = tf.placeholder(tf.float32)
x_image = tf.reshape(xs, [-1, 1, 16, 5])

##conv2d layer =1#
W_conv1 = WeightVariable([1,2,5,10])
b_conv1 = BiasVariable([10])
h_conv1 = tf.nn.relu(Conv2d(x_image, W_conv1)+b_conv1)
h_pool1 = MaxPool2x2(h_conv1)

##conv2d layer = 2#
W_conv2 = WeightVariable([1,2,10,20])
b_conv2 = BiasVariable([20])
h_conv2 = tf.nn.relu(Conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = MaxPool2x2(h_conv2)

#conv2d layer = 3#
W_conv3 = WeightVariable([1,2,20,40])
b_conv3 = BiasVariable([40])
h_conv3 = tf.nn.relu(Conv2d(h_pool2, W_conv3) + b_conv3)
h_pool3 = MaxPool2x2(h_conv3)

#conv2d layer = 4#
W_conv4 = WeightVariable([1,2,40,80])
b_conv4 = BiasVariable([80])
h_conv4 = tf.nn.relu(Conv2d(h_pool3, W_conv4) + b_conv4)
h_pool4 = MaxPool2x2(h_conv4)

## full connect layer =1#
W_fc1 = WeightVariable([1*1*80, 32])
b_fc1 = BiasVariable([32])
h_pool4_flat = tf.reshape(h_pool4, [-1, 1*1*80])
h_fc1 = tf.nn.relu(tf.matmul(h_pool4_flat, W_fc1) + b_fc1)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

W_fc2 = WeightVariable([32, 2])
b_fc2 = BiasVariable([2])
prediction = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2)+b_fc2)

cross_entropy = tf.reduce_mean(-tf.reduce_sum(ys * tf.log(tf.clip_by_value(prediction, 1e-7, 1.0)),
                                              reduction_indices=[1]))


train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

saver = tf.train.Saver()

sess = tf.Session()

init = tf.global_variables_initializer()
sess.run(init)

ckpt = tf.train.get_checkpoint_state('NetworkSaver/')
if ckpt and ckpt.model_checkpoint_path:
    saver.restore(sess, ckpt.model_checkpoint_path)
    print('Network Restore (%s) ok! ...' %(ckpt.model_checkpoint_path))
    #储存成中间格式可以网站上使用
#    conv1_weight = sess.run(W_conv1)
#    conv1_bias = sess.run(b_conv1)
#    conv2_weight = sess.run(W_conv2)
#    conv2_bias = sess.run(b_conv2)
#    conv3_weight = sess.run(W_conv3)
#    conv3_bias = sess.run(b_conv3)
#    conv4_weight = sess.run(W_conv4)
#    conv4_bias = sess.run(b_conv4)
#    fc1_weight = sess.run(W_fc1)
#    fc1_bias = sess.run(b_fc1)
#    fc2_weight = sess.run(W_fc2)
#    fc2_bias = sess.run(b_fc2)
#    np.save('NetworkSaver/conv1_weight.npy', conv1_weight)
#    np.save('NetworkSaver/conv1_bias.npy', conv1_bias)
#    np.save('NetworkSaver/conv2_weight.npy', conv2_weight)
#    np.save('NetworkSaver/conv2_bias.npy', conv2_bias)
#    np.save('NetworkSaver/conv3_weight.npy', conv3_weight)
#    np.save('NetworkSaver/conv3_bias.npy', conv3_bias)     
#    np.save('NetworkSaver/conv4_weight.npy', conv4_weight)
#    np.save('NetworkSaver/conv4_bias.npy', conv4_bias)
#    np.save('NetworkSaver/fc1_weight.npy', fc1_weight)
#    np.save('NetworkSaver/fc1_bias.npy', fc1_bias)     
#    np.save('NetworkSaver/fc2_weight.npy', fc2_weight)
#    np.save('NetworkSaver/fc2_bias.npy', fc2_bias)       


#输入需要预测的指数代码
indexList = []
possDict = {}
while True:
    i = input('Input Index Code (Enter For End) : ')
    if i=='':
        print('\n')
        break
    indexList.append(i)
    possDict[i] = []
    
KDAYS = 16
    
while True:
   
    for code in indexList:
        
        df = ts.get_k_data(code, index=True)
        del df['date']
        del df['code']
        l = len(df)
        df = df[l-KDAYS:l]
        kdatapart = df.reset_index(drop=True)
        lowlist = []
        highlist = []
        volumelist = []
        feeddata = []
        for j in range(0, len(kdatapart)):
            lowlist.append(float(kdatapart['low'][j]))
            highlist.append(float(kdatapart['high'][j]))
            volumelist.append(float(kdatapart['volume'][j]))
        low_min = min(lowlist)
        low_max = max(highlist)
        volume_min = min(volumelist)
        volume_max = max(volumelist)
        for j in range(0, len(kdatapart)):
            fopen = float(kdatapart['open'][j])
            fclose = float(kdatapart['close'][j])
            fhigh = float(kdatapart['high'][j])
            flow = float(kdatapart['low'][j])
            fvolume = float(kdatapart['volume'][j])
            unified_open = (fopen-low_min)/(low_max-low_min)
            unified_close = (fclose-low_min)/(low_max-low_min)
            unified_high = (fhigh-low_min)/(low_max-low_min)
            unified_low = (flow-low_min)/(low_max-low_min)
            unified_vol = (fvolume-volume_min)/(volume_max-volume_min)
            feeddata.append(unified_open)
            feeddata.append(unified_close)
            feeddata.append(unified_high)
            feeddata.append(unified_low)
            feeddata.append(unified_vol)
        inputData = np.array(feeddata).reshape(1, KDAYS*5)
        currPred = sess.run(prediction, feed_dict={xs:inputData, keep_prob:1})
        upPoss = currPred[0][0]
        downPoss = currPred[0][1]
        print('Index : %s , Up Chance: %0.2f%% ' %(code, upPoss*100))
        possDict[code].append(upPoss)
    
    plt.figure(figsize=(12,7))
    plt.title('Up Possibilty Chart\n')
    plt.xlabel('Time')
    plt.ylabel('Possibilty')
    
    for code in possDict.keys():
        possList = possDict[code]
        plt.plot(possList, linewidth=2.0, label=code)
    
    plt.legend(loc='upper left')
    plt.show()
    
    print('\n Wait For 1 Minute ... \n')
    time.sleep(60)
    