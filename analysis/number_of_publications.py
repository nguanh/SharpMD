import pandas
import os
import matplotlib.pyplot as plt
local_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(local_path,"data")

def get_mean(name,series):
    sum = 0
    total = 0
    for index, row in series.iterrows():
        sum += index * row.amount
        total += row.amount

    print(name,sum / total)

def get_meanx(name,series):
    sum = 0
    total = 0
    for index, row in series.iterrows():
        tmp = row['counter']
        sum += index * tmp
        total += row['counter']

    print(name,sum / total)

#Anzahl an publikationen, die ein Autor rausbringt

pub_date_dblp = pandas.read_csv(os.path.join(data_path, "amount_of_pub_dblp.csv"), index_col='counter')
pub_date_arxiv = pandas.read_csv(os.path.join(data_path, "amount_of_pub_arxiv.csv"), index_col='counter')
pub_date_citeseerx = pandas.read_csv(os.path.join(data_path, "amount_of_pub_citeseer.csv"), index_col='counter')


num_aut_dblp = pandas.read_csv(os.path.join(data_path, "number_author_dblp.csv"), index_col='amount')
num_aut_arxiv = pandas.read_csv(os.path.join(data_path, "number_author_arxiv.csv"), index_col='amount')
num_aut_citeseerx = pandas.read_csv(os.path.join(data_path, "number_author_citeseerx.csv"), index_col='amount')

get_mean("DBLP", pub_date_dblp)
get_mean("ARXIV", pub_date_arxiv)
get_mean("CITESEERX", pub_date_citeseerx)

get_meanx("DBLP AUT", num_aut_dblp)
get_meanx("ARXIV AUT", num_aut_arxiv)
get_meanx("CITESEERX AUT", num_aut_citeseerx)

print("DBLP AUT MAX", num_aut_dblp.idxmax(0))
print("ARXIV AUT MAX", num_aut_arxiv.idxmax(1))
print("CITESEERX AUT MAX", num_aut_citeseerx.idxmax(1))