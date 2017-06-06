
import pandas
import matplotlib.pyplot as plt
import os
# 1 tunnel zu mysqldb
local_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(local_path,'data')

career_dblp = pandas.Series.from_csv(os.path.join(file_path,"career_dblp.csv"))
career_length_dblp = pandas.Series.from_csv(os.path.join(file_path,"career_length_dblp.csv"))
career_mean_dblp = pandas.Series.from_csv(os.path.join(file_path,"career_mean_dblp.csv"))

career_arxiv = pandas.Series.from_csv(os.path.join(file_path,"career_arxiv.csv"))
career_length_arxiv = pandas.Series.from_csv(os.path.join(file_path,"career_length_arxiv.csv"))
career_mean_arxiv = pandas.Series.from_csv(os.path.join(file_path,"career_mean_arxiv.csv"))

mean_dblp = []
mean_arxiv = []
for absolut,relativ in zip(career_dblp,career_mean_dblp):
    mean_dblp.append(absolut / relativ)


for absolut,relativ in zip(career_arxiv,career_mean_arxiv):
    mean_arxiv.append(absolut/relativ)

mean_series_dblp = pandas.Series(mean_dblp)
mean_series_arxiv = pandas.Series(mean_arxiv)

fig, axes = plt.subplots(nrows=1, ncols=2)


"""
axis1 = mean_series_dblp.plot(ax=axes[0])
axis1.set_xlabel("Years of Work")
axis1.set_ylabel("Mean Publications")
axis1.set_xlim(0, 80)

axis1 = mean_series_arxiv.plot(ax=axes[1])
axis1.set_xlabel("Years of Work")
axis1.set_ylabel("Mean Publications")
axis1.set_xlim(0, 80)

axes[0].set_title('DBLP')
axes[1].set_title('ArXiv')
plt.suptitle("Mean Publications Per Year of Work")
"""
"""
axis = career_length_dblp.plot(ax=axes[0])
axis.set_xlabel("Years of Work")
axis.set_ylabel("Authors")
axis.set_xlim(0, 50)
axis.set_ylim(0, 200000)

axis2 = career_length_arxiv.plot(ax=axes[1])
axis2.set_xlabel("Years of Work")
axis2.set_ylabel("Authors")
axis2.set_xlim(0, 50)
axis2.set_ylim(0, 200000)
axes[0].set_title('DBLP')
axes[1].set_title('ArXiv')
plt.suptitle("Author Career Duration")
"""
axis = career_dblp.plot(ax=axes[0])
axis.set_xlabel("Years of Work")
axis.set_ylabel("Authors")


axis2 = career_arxiv.plot(ax=axes[1])
axis2.set_xlabel("Years of Work")
axis2.set_ylabel("Authors")

axes[0].set_title('DBLP')
axes[1].set_title('ArXiv')
plt.suptitle("Author Career Duration")
plt.show()
