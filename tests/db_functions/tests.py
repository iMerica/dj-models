from djmodels.db.models import CharField, Value as V
from djmodels.db.models.functions import Coalesce, Length, Upper
from djmodels.test import TestCase

from .models import Author


class FunctionTests(TestCase):

    def test_nested_function_ordering(self):
        Author.objects.create(name='John Smith')
        Author.objects.create(name='Rhonda Simpson', alias='ronny')

        authors = Author.objects.order_by(Length(Coalesce('alias', 'name')))
        self.assertQuerysetEqual(
            authors, [
                'Rhonda Simpson',
                'John Smith',
            ],
            lambda a: a.name
        )

        authors = Author.objects.order_by(Length(Coalesce('alias', 'name')).desc())
        self.assertQuerysetEqual(
            authors, [
                'John Smith',
                'Rhonda Simpson',
            ],
            lambda a: a.name
        )

    def test_func_transform_bilateral(self):
        class UpperBilateral(Upper):
            bilateral = True

        try:
            CharField.register_lookup(UpperBilateral)
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__upper__exact='john smith')
            self.assertQuerysetEqual(
                authors.order_by('name'), [
                    'John Smith',
                ],
                lambda a: a.name
            )
        finally:
            CharField._unregister_lookup(UpperBilateral)

    def test_func_transform_bilateral_multivalue(self):
        class UpperBilateral(Upper):
            bilateral = True

        try:
            CharField.register_lookup(UpperBilateral)
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__upper__in=['john smith', 'rhonda'])
            self.assertQuerysetEqual(
                authors.order_by('name'), [
                    'John Smith',
                    'Rhonda',
                ],
                lambda a: a.name
            )
        finally:
            CharField._unregister_lookup(UpperBilateral)

    def test_function_as_filter(self):
        Author.objects.create(name='John Smith', alias='SMITHJ')
        Author.objects.create(name='Rhonda')
        self.assertQuerysetEqual(
            Author.objects.filter(alias=Upper(V('smithj'))),
            ['John Smith'], lambda x: x.name
        )
        self.assertQuerysetEqual(
            Author.objects.exclude(alias=Upper(V('smithj'))),
            ['Rhonda'], lambda x: x.name
        )
