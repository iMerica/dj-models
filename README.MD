## DJ Models

Django Models and Nothing Else. Use Django's ORM with any non-async web framework!

## Notes
- ⚠️  This does not work yet. Once it does, I'll publish to PyPi ⚠️  
- All Praise to the Django Dev Team


## Getting Started

Create an app directory for your models and settings (DB Connection Details) 

    mkdir app
    touch app/{__init__.py,models.py,settings.py}
    
    
Add your database settings to the settings module. See Django's Docs on this for more info.

```python
SECRET_KEY = '<ACTUAL SECRET KEY>'
DATABASES = {
    'default': {
        'ENGINE': 'djmodels.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'mysecretpassword',
        'HOST': '0.0.0.0',
        'PORT': '5432',
    }
}

INSTALLED_APPS = ['app']

```
    

Add a model to `app/models.py`

```python
from djmodels.db import models

class Person(models.Model):
    name = models.CharField()
    age = models.PositiveIntegerField()

```
Export your settings module

    export DJANGO_SETTINGS_MODULE=app.settings


Create migrations

    djmodels-admin makemigrations app
    

Run Migrate

    djmodels-admin migrate app
    

Import the model and make queries

```python

from flask import Flask
from app.models import Person
app = Flask(__name__)

@app.route("/person/")
def get_random_person():
    person = Person.objects.order_by('?').first()
    return '{}'.format(person.name)

``` 

## LICENSE
MIT 
