# Warning: Out of date.
cd $( dirname ${BASH_SOURCE[0]})
python ./make_venv.py
. ./activate.sh
python -m pip install pip --upgrade
python -m pip install -r requirements.txt --upgrade
python -m pip install -r requirements.testing.txt --upgrade
python -m pip install  -e . --upgrade