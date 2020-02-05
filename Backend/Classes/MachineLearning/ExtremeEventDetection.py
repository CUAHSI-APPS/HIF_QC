import math
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt

#Streaming peak over threshold with drift
def extreme_event_detection(df_series, d =-1): #input parameters are data frame and window length(d)
  
  if d == -1:
  	  d = int(df_series.count()/10)
  	  
  anomalies = [] #set of anomalies
  wStarX = [] #window
  m_avg = 0 #moving average of the window's next observation
  k = 0  
  df_series_200 = df_series[:200] #first 200 values of the data
  
  out = pot_kdd_paper(df_series_200.values) #POT method 
  z_q = out[0]
  t = out[1]
  N_t = out[2]
  y_t = out[3]
  n = out[4]

  df_series_200_norm = df_series_200[(df_series_200 <= z_q)] #first d normal values from the normal values
  x_win = df_series_200_norm.values[:d]
  wStarX.extend(x_win)
  m_avg = movAvg(wStarX) #moving average of the next observation after the window 
  xd = []
 
  #computing variable change for the next 300 observations
  for i in range (200, 500):	
	  xd.append(abs(df_series.values[i] - m_avg))
	  wStarX = np.delete(wStarX, 0)
	  wStarX = np.append(wStarX, df_series.values[i])
	  m_avg = movAvg(wStarX)

  out1 = pot_kdd_paper(xd) #POT method
  z_q = out1[0]
  t = out1[1]
  N_t = out1[2]
  y_t = out1[3]
  n = out1[4] 
  k = n
  
  output_list = []
  bool_list = [True for i in range(len(df_series))]
  for i in range(501, len(df_series.values)):  
      xd = np.append(xd, df_series.values[i] - m_avg) #variable change
      if xd[-1] >= z_q: #anomaly case
        anomalies.append((i,df_series.values[i],1))#adding anomaly to the anomalies set
        output_list.append((i,1))
        bool_list[i] = False
        m_avg = movAvg(wStarX)
      elif xd[-1] > t:	
    	  k = k+1 
    	  ans = pot_kdd_paper(xd) #POT method
    	  z_q = ans[0]
    	  t = ans[1]
    	  N_t = ans[2]
    	  y_t = ans[3]
    	  n = ans[4] 

    	  wStarX = np.delete(wStarX, 0)
    	  wStarX = np.append(wStarX, df_series.values[i])
    	  m_avg = movAvg(wStarX) #update of local model
      else: #normal value case
        k = k + 1
        output_list.append((i,0))
        wStarX = np.delete(wStarX, 0)
        wStarX = np.append(wStarX, df_series.values[i])
        m_avg = movAvg(wStarX) #update of local model
  return anomalies, output_list, bool_list


#get columns of the data set
def cols(data):
  columns = list(data.columns)
  return columns

#moving average function(to compute variable change)
def movAvg(wStarX):
    return np.mean(wStarX)

#Peak Over Threshold method
def pot_kdd_paper(x):
  t = np.percentile(x,95) #initial threshold is set to 95 percentile
  n_t = [i for i in x if i > t] 
  y_t = [i-t for i in n_t] 
  N_t = len(n_t)
  y_mean = float(sum(y_t))/(len(y_t))
  y_min = min(y_t)
  x_star = 2*(y_mean - y_min)/(y_min)**2  
  total = 0
  for i in y_t:
    total = total + math.log(1+x_star*i)
  v_x = 1 + (1/len(n_t))*total
  gam = v_x - 1
  sig = gam/float(x_star)
  n = len(x)
  asd = ((0.02*n)/N_t)**(-gam)
  z_q = t + sig*(asd-1)/gam
  return (z_q, t, N_t, y_t, n)



#to visualize data
#def visualize(df_series,anomalies):
#  ext = np.array(anomalies)
#  X_ext = ext[:,0]
#  y_ext = ext[:,1]
#  plt.plot(X_ext, y_ext, 'd', color= 'r')
#  y_value = df_series.values
#  x_axis = np.arange(len(y_value))
#  plt.plot(x_axis, y_value, '+', color= 'b')
# plt.show()

#to get a list of 1's(anomaly) or 0's(normal value) for each observation
def anomaly_binary_list(binary_output_of_extreme_event_detection_function):
  temp_list = np.array(binary_output_of_extreme_event_detection_function)
  binary_list = temp_list[:,1]
  # plt.plot(binary_list)
  # plt.show()
  return binary_list

