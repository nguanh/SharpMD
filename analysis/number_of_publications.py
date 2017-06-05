import pandas
import os
import matplotlib.pyplot as plt
local_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(local_path,"data")

#Anzahl an publikationen, die ein Autor rausbringt

pub_date_dblp = pandas.read_csv(os.path.join(data_path, "amount_of_pub_dblp.csv"), index_col='counter')
pub_date_arxiv = pandas.read_csv(os.path.join(data_path, "amount_of_pub_arxiv.csv"), index_col='counter')
pub_date_citeseerx = pandas.read_csv(os.path.join(data_path, "amount_of_pub_citeseer.csv"), index_col='counter')



fig, axes = plt.subplots(nrows=1, ncols=3)

axis = pub_date_dblp.plot.box(ax=axes[2])
axis2 = pub_date_arxiv.plot.box(ax=axes[1])
axis3 = pub_date_citeseerx.plot.box(ax=axes[0])

axes[0].set_title('CiteseerX')
axes[1].set_title('ArXiv')
axes[2].set_title('DBLP')
plt.show()
