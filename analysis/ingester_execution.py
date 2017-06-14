
import os
import pandas
import matplotlib.pyplot as plt
import re
local_path = os.path.dirname(os.path.abspath(__file__))
def display(path):
    file_path = os.path.join(local_path,'data',path)
    time_list = []
    limbo_list = []
    sum = float(0)
    with open(file_path,'r') as f:

        for line in f:
            if "TRACK:" in line:
                time_cost = float(line[line.index("TRACK:")+len("TRACK:"):])
                # filter out values caused by db reset
                if time_cost > 500:
                    time_list.append(360)
                else:
                    time_list.append(time_cost)
                sum += time_cost

            if "limbo " in line:
                m = re.findall('limbo(.*?)/', line, re.DOTALL)
                limbo = int(m[0].strip())
                limbo_list.append(limbo)



            # get seconds
    plot_data = pandas.Series(time_list, index=range(0, len(time_list) * 5000, 5000))
    limbo_data = pandas.Series(limbo_list, index=range(0, len(limbo_list) * 5000, 5000))
    print(limbo_data)

    print(sum)

    return [plot_data, limbo_data]


if __name__ =="__main__":
    """
    fig, axes = plt.subplots(nrows=1, ncols=2)
    dblp  = display("DBLP_Harvester.log")
    arxiv = display("arxiv-harvester.log")
    ax1=dblp.plot(ax=axes[0])
    ax2=arxiv.plot(ax=axes[1])

    ax1.set_xlim(0, 1000000)
    ax2.set_xlim(0, 1000000)

    axes[0].set_title('DBLP (BULK)')
    axes[1].set_title('ARXIV(OAI-PMH)')
    plt.suptitle("Harvester Execution Time")
    """


    ing0,lim0 = display("ingester2.log")
    ax1 = ing0.plot()
    #ax2 = ing1.plot(ax=axes[1])

    ax1.set_xlim(0, 1000000)
    #ax2.set_xlim(0, 1000000)

    ax1.set_ylim(0, 800)
    #ax2.set_ylim(0, 700)
    ax1.set_xlabel('Publications Harvested')
    ax1.set_ylabel('Time (s)')
    #axes[0].set_title('Empty Database')
    #axes[1].set_title('Populated Database')
    plt.suptitle("Ingester Execution Time")

    plt.show()

    #display("dblp-harvester-neu.log")
    #display("TESTDBLP.log")


