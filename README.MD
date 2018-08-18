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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'mydatabaseuser',
        'NAME': 'mydatabase',
        'TEST': {
            'NAME': 'mytestdatabase',
        },
    },
}
```
    

Add a model to `app/models.py`

```python
from djmodels.db import models

class Person(models.Model):
    name = models.CharField()
    age = models.PositiveIntegerField()

```

Create migrations

    DJANGO_SETTINGS_MODULE=app.settings djmodels-admin makemigrations app/models.py
    

Run Migrate

    DJANGO_SETTINGS_MODULE=app.settings djmodels-admin migrate app/models.py
    

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
