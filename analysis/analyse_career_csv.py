
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


"""
mean_series = pandas.Series(mean)
axis = mean_series.plot.bar(title="Mean Publications per year of career (DBLP)")
axis.set_xlabel("Years of Work")
axis.set_ylabel("Mean Publication per year")
axis.set_xlim(0, 80)
"""

axis = career_length_dblp.plot(title="Author Career Duration")
axis.set_xlabel("Years of Work")
axis.set_ylabel("Authors")
axis.set_xlim(0, 50)
axis.set_ylim(0, 200000)
#axis2 = career_dblp.plot.bar()
plt.show()
