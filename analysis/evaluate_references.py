import os
import re
import pandas
from ingester.helper import normalize_title
import pymysql

#TODO ausführlichere analysen
local_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(local_path,'data')
#list of MAG ids that have a valid pdf file
match_list=[
    "0AB5DA92",
    #"003D2ABA",
    "03A0D543",
    "5DE7D587",
    "015EEC82",
    "026E4E7E",
    #"41DE1CEC",
    "46EF8055",
    "0257F156",
    "01865193",
    "03729759",
    "473B91DE"]
    #"10726450"]
# list of pdf urls in the same order
pdf_url_list =[
    "http://discovery.ucl.ac.uk/1379646/2/PhD%20thesis%20-%20CAK%20Lange%20-%2012_2012.pdf",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1760723/pdf/147-0706429a.pdf",
    "http://eknygos.lsmuni.lt/springer/520/3-30.pdf",
    "https://repub.eur.nl/pub/23546/011024_Peters,%20Jeroen%20Wilhelmus%20Bernardus.pdf",
    "https://core.ac.uk/download/pdf/338126.pdf",
    "http://www.pgedf.ufpr.br/Referencias08/Faude%20SportsMed%202009%20SG%20Fisiologia.pdf",
    "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC4656104&blobtype=pdf",
    "http://www.luzimarteixeira.com.br/wp-content/uploads/2011/04/exercise-and-syndrome-x.pdf",
    "https://core.ac.uk/download/pdf/9633694.pdf",
    "http://www.ingentaconnect.com/content/wef/wer/1999/00000071/00000005/art00016?crawler=true",
]
def evaluate_references():
    total_count= 0
    overall_count = 0
    truepositive = 0
    falsepositive = 0
    missing_count = 0
    limbo = 0
    dec_id_list= [int(item, 16) for item in match_list ]
    fp_list = []
    ff_list = []
    db_list = []

    raw = pandas.read_csv(os.path.join(file_path, "count_ref.csv"), index_col='ID')
    raw = raw.drop_duplicates()

    # look up dict for titles
    titles = {}
    with open(os.path.join(file_path, 'ref.log'), encoding="utf8") as f:
        for line in f:
            re.findall(r'alpha(.*?)bravo', line)
            if 'SOURCE' in line:
                regex= r'SOURCE (.*?):'
            else:
                regex = r'REF (.*?):'
            try:
                id_match = re.findall(regex, line)[0]
                normal_id = int(id_match, 16)
                title = line[line.index(":")+1:]
                titles[normal_id] = title
            except:
                continue

    read_connector = pymysql.connect(user="root",
                                     password="master",
                                     host="localhost",
                                     database="storage",
                                     charset="utf8mb4")

    # copy references from db to list
    correct = open(os.path.join(file_path,'correct40.txt'), 'w',encoding="utf8")
    false = open(os.path.join(file_path, 'false40.txt'), 'w',encoding="utf8")
    missing = open(os.path.join(file_path, 'missing40.txt'), 'w', encoding="utf8")

    with read_connector.cursor() as cursor:
        cursor.execute("SELECT * from storage.ingester_pubreference",())
        for element in cursor:
            db_list.append({
                "id": element[0],
                "reference": element[1],
                "source": element[2],
                "title": element[3],
                "key": element[4],
                "match": False
            })

        cursor.execute("SELECT COUNT(*) FROM storage.weaver_singlereference WHERE  status='LIM'")
        for element in cursor:
            limbo = element[0]
    read_connector.close()
    for key, value in raw.iterrows():
        overall_count += 1
        # find true positives
        if value['source_paper'] in dec_id_list:
            # find matching db list entry
            total_count += 1
            count = 0
            for element1 in db_list:
                if element1['source'] == value['source_paper'] and element1['reference'] == value['ref_paper']:
                    source_title = titles[value['source_paper']].strip()
                    ref_title = titles[value['ref_paper']].strip()

                    correct.write("({},{})-->({},{})   [{},{}]\n".format(
                        value['source_paper'],
                        source_title,
                        value['ref_paper'],
                        ref_title,
                        element1['title'],
                        element1['key']
                    ))
                    element1['match'] = True
                    truepositive += 1
                    count = 5
                    break

            if count == 0:
                missing_count += 1
                ff_list.append({
                    "source": value['source_paper'],
                    "reference": value['ref_paper'],
                })

    for element2 in db_list:
        if element2['match'] is False:
            try:
                source_title = titles[element2['source']].strip()
                ref_title = titles[element2['reference']].strip()
            except KeyError as e:
                print("Missing key", e)
                falsepositive += 1
                continue
                # SONDERFALL
            if normalize_title(element2['title']) != normalize_title(ref_title):
                false.write("({},{})-->({},{})   [{},{}]\n".format(
                    element2['source'],
                    source_title,
                    element2['reference'],
                    ref_title,
                    element2['title'],
                    element2['key'],
                ))
                falsepositive += 1
            else:
                correct.write("({},{})-->({},{})   [{},{}]\n".format(
                    value['source_paper'],
                    source_title,
                    value['ref_paper'],
                    ref_title,
                    element1['title'],
                    element1['key']
                ))
                truepositive += 1



    for element in ff_list:
            source = element['source'],
            source_title = titles[element['source']].strip()
            try:
                ref_title = titles[element['reference']].strip()
                missing.write("({},{})-->({},{})\n".format(
                    source,
                    source_title,
                    element['reference'],
                    ref_title,
                ))
            except Exception as e:
                print(e)
                continue

    correct.close()
    false.close()
    missing.close()

    print("Overall           : {}".format(overall_count))
    print("Total             : {}".format(total_count,truepositive,falsepositive))
    print("True Positive     : {}".format(truepositive))
    print("False Positive    : {}".format(falsepositive))
    print("Missing           : {}".format(missing_count))
    print("Limbo             : {}".format(limbo))



if __name__=="__main__":
    evaluate_references()