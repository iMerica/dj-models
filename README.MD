# DJ Models

Use the Django ORM in any Python web framework.

## Install

    pip3 install djmodels

 
## Getting Started

Create an app directory for your models and settings (DB connection details).

    mkdir -p project/base
    touch project/base/{__init__.py,models.py}
    touch settings.py
    
    
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

INSTALLED_APPS = ['base']

```
    

Add a model to `app/models.py`

```python
from djmodels.db import models

class Person(models.Model):
    name = models.CharField()
    age = models.PositiveIntegerField()

```
Export your settings module

    export DJMODELS_SETTINGS_MODULE=app.settings


Create migrations

    $ /manage.py makemigrations base
    # Migrations for 'app':
    #   - Create model Person 
    

Run Migrate

    $ /manage.py makemigrations base
    # Operations to perform:
    #   Apply all migrations: base
    #   Running migrations:
    #       Applying base.0001_initial... OK
    

Import the model into any webframework and make queries. For example, Flask.

```python

from flask import Flask
import djmodels

djmodels.setup()
from app.models import Person
app = Flask(__name__)

@app.route("/person/")
def get_random_person():
    person = Person.objects.order_by('?').first()
    return '{}'.format(person.name)

``` 

### Example Apps

- [Flask + DjModels](https://github.com/iMerica/dj-models-demo)

## Gotchas

- Make sure to set DJMODELS_SETTINGS_MODULE is set!


## LICENSE
MIT 
