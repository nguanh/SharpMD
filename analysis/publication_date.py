import pandas
import os
import matplotlib.pyplot as plt
local_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(local_path,"data")


pub_date_dblp = pandas.read_csv(os.path.join(data_path, "pub_year_dblp.csv"), index_col='year')
pub_date_arxiv = pandas.read_csv(os.path.join(data_path, "pub_year_arxiv.csv"), index_col='year')
pub_date_citeseerx = pandas.read_csv(os.path.join(data_path, "pub_year_citeseerx.csv"), index_col='year')



fig, axes = plt.subplots(nrows=1, ncols=3)

axis = pub_date_dblp.plot(ax=axes[2])
axis2 = pub_date_arxiv.plot(ax=axes[1])
axis3 = pub_date_citeseerx.plot(ax=axes[0])
axis.set_ylim(0, 100000)
axes[0].set_title('CiteseerX')
axes[1].set_title('ArXiv')
axes[2].set_title('DBLP')
plt.show()
