# Steps to run the Address Book project

1) Clone the addressbook repo on your machine.
```
git clone https://github.com/divyeshrabadiya07/addressbook.git
```

2) To manage dependency, Create Virtual environment in root folder and activate it.
```
# create virtual environment
python -m venv venv

# activate it
.\venv\Scripts\activate
```

3) Install required Python modules from requirements.txt file
```
pip install -r requirements.txt
```

4) Run the server
```
uvicorn main:app --reload
```

5) Once server is started, Go to browser and hit the below URL
```
http://127.0.0.1:8000/docs
```

6) It will open the Swagger page. Go to every endpoint and test one by one.
