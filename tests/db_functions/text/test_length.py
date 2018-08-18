from djmodels.db.models import CharField
from djmodels.db.models.functions import Length
from djmodels.test import TestCase

from ..models import Author


class LengthTests(TestCase):

    def test_basic(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(
            name_length=Length('name'),
            alias_length=Length('alias'),
        )
        self.assertQuerysetEqual(
            authors.order_by('name'), [(10, 6), (6, None)],
            lambda a: (a.name_length, a.alias_length)
        )
        self.assertEqual(authors.filter(alias_length__lte=Length('name')).count(), 1)

    def test_ordering(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='John Smith', alias='smithj1')
        Author.objects.create(name='Rhonda', alias='ronny')
        authors = Author.objects.order_by(Length('name'), Length('alias'))
        self.assertQuerysetEqual(
            authors, [
                ('Rhonda', 'ronny'),
                ('John Smith', 'smithj'),
                ('John Smith', 'smithj1'),
            ],
            lambda a: (a.name, a.alias)
        )

    def test_transform(self):
        try:
            CharField.register_lookup(Length)
            Author.objects.create(name='John Smith', alias='smithj')
            Author.objects.create(name='Rhonda')
            authors = Author.objects.filter(name__length__gt=7)
            self.assertQuerysetEqual(
                authors.order_by('name'), ['John Smith'],
                lambda a: a.name
            )
        finally:
            CharField._unregister_lookup(Length)
