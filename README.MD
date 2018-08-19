# DJ Models

Use the Django ORM in any Python web framework.

## ⚠️ Notes ⚠️
- This is not ready yet. Once it is, I'll publish to PyPi.
- Async is not supported.
- All Praise to the Django dev team 

## Getting Started

Create an app directory for your models and settings (DB connection details).

    mkdir app
    touch app/{__init__.py,models.py,settings.py}
    
    
Add your database settings to the settings module. See Django's docs on this for more info.

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

    $ djmodels-admin makemigrations app
    # Migrations for 'app':
    #   - Create model Person 
    

Run Migrate

    $ djmodels-admin migrate app
    # Operations to perform:
    #   Apply all migrations: app
    #   Running migrations:
    #       Applying app.0001_initial... OK
    

Import the model into any webframework and make queries. For example, Flask.

```python

from flask import Flask
from app.models import Person
app = Flask(__name__)

@app.route("/person/")
def get_random_person():
    person = Person.objects.order_by('?').first()
    return '{}'.format(person.name)

``` 

## Bugs
- Migration files are currently being saved to a directory that is relative to the library itself rather than locally in main app/project directory. 


## LICENSE
MIT 
