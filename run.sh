set -e
if [[ ! -d venv ]]
then
    echo "Creating virtual environment 'venv' "
    python -m venv venv
    echo "Activating virtual environment 'venv' "
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python manage.py runserver

