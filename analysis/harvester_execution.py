
import os
import pandas
import matplotlib.pyplot as plt
local_path = os.path.dirname(os.path.abspath(__file__))
def display(path):
    file_path = os.path.join(local_path,'data',path)
    time_list = []
    with open(file_path,'r') as f:

        for line in f:
            if "TRACK:" not in line:
                continue

            time_cost = float(line[line.index("TRACK:")+len("TRACK:"):])
            time_list.append(time_cost)
            #plot_data =plot_data.append(pandas.Series([time_cost]), ignore_index=True)

            # get seconds
    plot_data = pandas.Series(time_list, index=range(0, len(time_list) * 500, 500))
    #sorted view
    # plot_data = pandas.Series(sorted(time_list,key=float), index=range(0,len(time_list)*500,500))



    axis =plot_data.plot()
    axis.set_ylim(0,32)
    plt.show()
if __name__ =="__main__":
    display("DBLP_Harvester.log")
