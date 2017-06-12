import pandas
import matplotlib.pyplot as plt


data = pandas.DataFrame([
    {
        "Threshold": 100,
        "True Positive": 36,
        "False Positive": 0
    },
    {
     "Threshold": 90,
     "True Positive": 53,
     "False Positive": 1
    },
    {
        "Threshold": 80,
        "True Positive": 54,
        "False Positive": 1
    },
    {
        "Threshold": 70,
        "True Positive": 55,
        "False Positive": 2
    },
    {
        "Threshold": 60,
        "True Positive": 57,
        "False Positive": 7
    },
    {
        "Threshold": 50,
        "True Positive": 62,
        "False Positive": 33
    },
    {
        "Threshold": 40,
        "True Positive": 63,
        "False Positive": 169
    },
    {
        "Threshold": 30,
        "True Positive": 50,
        "False Positive": 594
    },

]
)

data.set_index('Threshold', inplace=True)
overall = 78-15

for key, value in data.iterrows():
    p = float(value['True Positive']) /float(value['False Positive'] +value['True Positive'])
    r = float(value['True Positive']) /float(value['True Positive'] +overall)
    F1=2*float((p*r)/(p+r))
    print(key,F1)


data.plot()
plt.show()

