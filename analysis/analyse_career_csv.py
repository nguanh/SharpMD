
import pandas
import matplotlib.pyplot as plt
import os
# 1 tunnel zu mysqldb
local_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(local_path,'data')

career_dblp = pandas.Series.from_csv(os.path.join(file_path,"career_dblp.csv"))
career_length_dblp = pandas.Series.from_csv(os.path.join(file_path,"career_length_dblp.csv"))
career_mean_dblp = pandas.Series.from_csv(os.path.join(file_path,"career_mean_dblp.csv"))

#career_dblp.plot()
mean = []
for absolut,relativ in zip(career_dblp,career_mean_dblp):
    mean.append(absolut/relativ)
    print(absolut,relativ)


mean_series = pandas.Series(mean)
mean_series.plot.bar()
#career_length_dblp.plot.bar()
plt.show()