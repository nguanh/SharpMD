
import os
import pandas
import matplotlib.pyplot as plt
local_path = os.path.dirname(os.path.abspath(__file__))
def display(path):
    file_path = os.path.join(local_path,'data',path)
    time_list = []
    sum_list = []
    sum = float(0)
    counter = 1
    sum_time = 0
    with open(file_path,'r') as f:

        for line in f:
            if "TRACK:" not in line:
                continue

            time_cost = float(line[line.index("TRACK:")+len("TRACK:"):])

            sum += time_cost
            sum_time += time_cost
            if counter % 10 == 0:
                time_list.append(sum_time)
                sum_time = 0
            counter += 1

            # get seconds
    plot_data = pandas.Series(time_list, index=range(0, len(time_list) * 5000, 5000))
    print(sum)

    return plot_data


if __name__ =="__main__":

    fig, axes = plt.subplots(nrows=1, ncols=2)
    dblp  = display("DBLP_Harvester.log")
    arxiv = display("arxiv-harvester.log")
    ax1=dblp.plot(ax=axes[0])
    ax2=arxiv.plot(ax=axes[1])

    ax1.set_xlim(0, 1000000)
    ax2.set_xlim(0, 1000000)

    ax1.set_ylim(0, 150)
    ax2.set_ylim(0, 150)

    axes[0].set_title('DBLP (BULK)')
    axes[1].set_title('ARXIV(OAI-PMH)')
    axes[0].set_xlabel('Publications Harvested')
    axes[0].set_ylabel('Time (s)')
    axes[1].set_xlabel('Publications Harvested')
    axes[1].set_ylabel('Time (s)')
    plt.suptitle("Harvester Execution Time")

    plt.show()



