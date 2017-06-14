INSTALLATION

Benötigt: Ubuntu ( wurde mit 16.04 getestet)


1.MariaDB installieren:

sudo apt-get install mariadb-server
sudo service mysql stop
sudo mysql_install_db
sudo service mysql start
sudo mysql_secure_installation
ODER
install_mariadb.sh script in scripts folder ausführen

user und passwort festlegen

>Optional, um user anzulegen:
>>User anzeigen lassen:
>>SELECT User,Host FROM mysql.user;
>>In der Konsole den standard root löschen:
>>DROP USER 'root'@'localhost';
>>Root neu anlegen
>>CREATE USER 'root'@'localhost' IDENTIFIED BY '';
>>GRANT ALL PRIVILEGES ON *.* TO 'root'@'locahost';
>>FLUSH PRIVILEGES;
>>Passwort festlegen:
>>SET PASSWORD FOR root@localhost=PASSWORD('master');
>>FLUSH PRIVILEGES;

2. Python einrichten
setup_python.sh script mit parameter ausführen (unbedingt mit source ausführen!):

source setup_python.sh sharp-env
Dies erzeugt eine virtuelle python umgebung, die im ordner <sharp-env> liegt
zum aktivieren eingeben
source /sharp_env/bin/activate
Dies muss jedes mal eingegeben werden, wenn SharpMD skript ausgeführt werden sollen


3. Django backend einrichten
 dazu das reset-djanso.sh skript ausführen und zusätzlich
 mysql -u root -p < create_fulltext_index.sql
 Um die indexe einzurichten. Falls root kein user ist, bitte anderen user angeben

4. Anpassen der globalen config
in SharpMD/conf/global_config.ini unter MARIADB und MARIADBX username und passwort eintragen
und nochmal die daten unter SharpMD/my.cnf eintragen

5. django starten
Hierzu gibt es einige aliases, die hinzugefügt werden können. Dabei wird ausgegangen, dass
der SharpMD ordner unter /home/nguyen/ liegt.
Neben Django muss auch die task queue und der scheduler gestartet werden.

#Alias zum starten der Virtuellen umgebung, die im Schritt 2. angelegt wurde
alias pythonmode='source /home/nguyen/sharp-env/bin/activate'

#Alias zum Starten von Django
alias djangostart='pythonmode; python3 /home/nguyen/SharpMD/manage.py runserver'

#Start der Task queue
alias celeryworker='cd /home/nguyen/SharpMD; celery worker -A SharpMD -l info --beat -S django'

#start des task queue schedulers
alias beatscheduler='cd /home/nguyen/SharpMD; celery -A SharpMD beat -l info -S django'

6. grobid einrichten
Grobid herunterladen und entpacken:
https://github.com/kermitt2/grobid

#grobid starten
alias grobid='cd /home/nguyen/grobid/grobid-service; mvn -Dmaven.test.skip=true jetty:run-war'



7. Zugriff auf backend:
Das front end ist erreichbar unter localhost:8000, wenn es gestartet wurde.
Das backend unter localhost:8000/admin/


8. Weaver starten
Für den Weaver müssen PDF und Referenz modul jeweils als task gespeichert werden.
Dazu im Django Backend--> Django-Celery_Beat-->Periodic Tasks  Add Periodic Task auswählen.

Als task weaver.tasks.pdfdownloader und bei interval ein intervall von mindestens 10 minute auswählen und task anlegen.
Das Gleiche nochmal für das Referenzierungsmodul mit weaver.tasks.referencertask




ORDNERSTRUKTUR:
> SharpMD          enthält Django-spezifische Dateien und Konfigurationen
> analysis         python skripte, die für die evaluation verwendet wurden
> conf             wrapper klasse für die globale Konfigurationsdatei
> dblp             alle Submodule(harvester,ingester) implementierungs für DBLP
> fileDownloader   Klasse zum herunterladen von dateien, wird für DBLP-XML download verwendet
> harvester        Harvester implementierung
> ingester         Ingester implementierung
> logs             hier werden log dateien abgelegt
> mysqlWrapper     Wrapper Klasse, die direkten MariaDB zugang regelt
> oai              alle Submodule für CiteseerX und ArXiv
> static           Ordner für statische Dateien(Bilder,css)  von django
> weaver           Weaver implementierung



HARVESTER:
Der Dblp Harveser braucht zusätzliche parameter dazu folgenden unter "extra config" eintragen:

{"zip_name": "dblp.xml.gz",
  "dtd_name": "dblp.dtd",
  "xml_name": "dblp.xml",
  "extraction_path": "/home/nguyen/raw_file/",
  "tags":["article","inproceedings","phdthesis","mastersthesis"]
}
extraction path ist der ordner, wo optionale dateien abgelegt werden sollen