
import os
import pandas
import matplotlib.pyplot as plt
local_path = os.path.dirname(os.path.abspath(__file__))
def display(path):
    file_path = os.path.join(local_path,'data',path)
    time_list = []
    sum_list = []
    sum = 0
    with open(file_path,'r') as f:

        for line in f:
            if "TRACK:" not in line:
                continue

            time_cost = float(line[line.index("TRACK:")+len("TRACK:"):])
            time_list.append(time_cost)
            sum += time_cost
            sum_list.append(sum)
            #plot_data =plot_data.append(pandas.Series([time_cost]), ignore_index=True)

            # get seconds
    plot_data = pandas.Series(time_list, index=range(0, len(time_list) * 500, 500))
    sum_data = pandas.Series(sum, index=range(0, len(time_list) * 500, 500))
    #sorted view
    # plot_data = pandas.Series(sorted(time_list,key=float), index=range(0,len(time_list)*500,500))
    print(plot_data)



    axis =plot_data.plot()
    #axis.set_ylim(0,32)
    #axis.set_xlim(0, 1000000)
    plt.show()
if __name__ =="__main__":
    display("DBLP_Harvester.log")
    display("dblp-harvester-neu.log")
    #display("TESTDBLP.log")
    #display("arxiv-harvester.log")
    #display("ingester.log")
