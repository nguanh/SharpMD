
import pandas
import matplotlib.pyplot as plt
import os
# 1 tunnel zu mysqldb
local_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(local_path,'data')

dblp = pandas.Series.from_csv(os.path.join(file_path,"exit_rate_dblp.csv"))
arxiv = pandas.Series.from_csv(os.path.join(file_path,"exit_rate_arxiv.csv"))


# divide
dblp /=dblp[0]
arxiv /=arxiv[0]

fig, axes = plt.subplots(nrows=1, ncols=2)

axis1 = dblp.plot.bar(ax=axes[0])
axis1.set_xlabel("Years of Work")
axis1.set_ylabel("Continuation")
axis1.set_xlim(0, 20)

axis1 = arxiv.plot.bar(ax=axes[1])
axis1.set_xlabel("Years of Work")
axis1.set_ylabel("Continuation")
axis1.set_xlim(0, 20)

axes[0].set_title('DBLP')
axes[1].set_title('ArXiv')
plt.suptitle("Continuation of Scientific Career")


plt.show()
