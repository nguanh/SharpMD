import pandas
import os
import matplotlib.pyplot as plt
local_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(local_path,"data")

#Anzahl an publikationen, die ein Autor rausbringt

pub_date_dblp = pandas.read_csv(os.path.join(data_path, "amount_of_pub_dblp.csv"), index_col='counter')
pub_date_arxiv = pandas.read_csv(os.path.join(data_path, "amount_of_pub_arxiv.csv"), index_col='counter')
pub_date_citeseerx = pandas.read_csv(os.path.join(data_path, "amount_of_pub_citeseer.csv"), index_col='counter')

sum = 0
total = 0
for index, row in pub_date_citeseerx.iterrows():
    sum += index*row.amount
    total += row.amount

print(sum/total)
