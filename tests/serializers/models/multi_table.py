from djmodels.db import models


class ParentManager(models.Manager):
    def get_by_natural_key(self, parent_data):
        return self.get(parent_data=parent_data)


class Parent(models.Model):
    parent_data = models.CharField(max_length=30, unique=True)

    objects = ParentManager()

    def natural_key(self):
        return (self.parent_data,)


class Child(Parent):
    child_data = models.CharField(max_length=30, unique=True)
