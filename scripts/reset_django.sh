cd /home/nguyen/SharpMD
echo 'Reset Django Database' 
python manage.py reset_db --router=default
echo 'Creating Django Tables'
python manage.py migrate
echo 'Importing initial database records'
python manage.py loaddata initial_data.json
echo 'Creating Admin accounts'
python manage.py createsuperuser
