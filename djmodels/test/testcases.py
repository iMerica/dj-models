import sys
import unittest
from collections import Counter
from contextlib import contextmanager
from copy import copy
from functools import wraps
from urllib.parse import (
    parse_qsl, urlencode, urlparse, urlunparse,
)

from djmodels.apps import apps
from djmodels.conf import settings
from djmodels.core.exceptions import ValidationError
from djmodels.core.files import locks
from djmodels.core.management import call_command
from djmodels.core.management.color import no_style
from djmodels.core.management.sql import emit_post_migrate_signal
from djmodels.db import DEFAULT_DB_ALIAS, connection, connections, transaction
from djmodels.test.client import Client
from djmodels.test.signals import setting_changed, template_rendered
from djmodels.test.utils import (
    CaptureQueriesContext, ContextList, modify_settings,
    override_settings,
)


__all__ = ('TestCase', 'TransactionTestCase',
           'SimpleTestCase', 'skipIfDBFeature', 'skipUnlessDBFeature')


def to_list(value):
    """
    Put value into a list if it's not already one. Return an empty list if
    value is None.
    """
    if value is None:
        value = []
    elif not isinstance(value, list):
        value = [value]
    return value


class _AssertNumQueriesContext(CaptureQueriesContext):
    def __init__(self, test_case, num, connection):
        self.test_case = test_case
        self.num = num
        super().__init__(connection)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            return
        executed = len(self)
        self.test_case.assertEqual(
            executed, self.num,
            "%d queries executed, %d expected\nCaptured queries were:\n%s" % (
                executed, self.num,
                '\n'.join(
                    '%d. %s' % (i, query['sql']) for i, query in enumerate(self.captured_queries, start=1)
                )
            )
        )


class _AssertTemplateUsedContext:
    def __init__(self, test_case, template_name):
        self.test_case = test_case
        self.template_name = template_name
        self.rendered_templates = []
        self.rendered_template_names = []
        self.context = ContextList()

    def on_template_render(self, sender, signal, template, context, **kwargs):
        self.rendered_templates.append(template)
        self.rendered_template_names.append(template.name)
        self.context.append(copy(context))

    def test(self):
        return self.template_name in self.rendered_template_names

    def message(self):
        return '%s was not rendered.' % self.template_name

    def __enter__(self):
        template_rendered.connect(self.on_template_render)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        template_rendered.disconnect(self.on_template_render)
        if exc_type is not None:
            return

        if not self.test():
            message = self.message()
            if self.rendered_templates:
                message += ' Following templates were rendered: %s' % (
                    ', '.join(self.rendered_template_names)
                )
            else:
                message += ' No template was rendered.'
            self.test_case.fail(message)


class _AssertTemplateNotUsedContext(_AssertTemplateUsedContext):
    def test(self):
        return self.template_name not in self.rendered_template_names

    def message(self):
        return '%s was rendered.' % self.template_name


class _CursorFailure:
    def __init__(self, cls_name, wrapped):
        self.cls_name = cls_name
        self.wrapped = wrapped

    def __call__(self):
        raise AssertionError(
            "Database queries aren't allowed in SimpleTestCase. "
            "Either use TestCase or TransactionTestCase to ensure proper test isolation or "
            "set %s.allow_database_queries to True to silence this failure." % self.cls_name
        )


class SimpleTestCase(unittest.TestCase):

    # The class we'll use for the test client self.client.
    # Can be overridden in derived classes.
    client_class = Client
    _overridden_settings = None
    _modified_settings = None

    # Tests shouldn't be allowed to query the database since
    # this base class doesn't enforce any isolation.
    allow_database_queries = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls._overridden_settings:
            cls._cls_overridden_context = override_settings(**cls._overridden_settings)
            cls._cls_overridden_context.enable()
        if cls._modified_settings:
            cls._cls_modified_context = modify_settings(cls._modified_settings)
            cls._cls_modified_context.enable()
        if not cls.allow_database_queries:
            for alias in connections:
                connection = connections[alias]
                connection.cursor = _CursorFailure(cls.__name__, connection.cursor)
                connection.chunked_cursor = _CursorFailure(cls.__name__, connection.chunked_cursor)

    @classmethod
    def tearDownClass(cls):
        if not cls.allow_database_queries:
            for alias in connections:
                connection = connections[alias]
                connection.cursor = connection.cursor.wrapped
                connection.chunked_cursor = connection.chunked_cursor.wrapped
        if hasattr(cls, '_cls_modified_context'):
            cls._cls_modified_context.disable()
            delattr(cls, '_cls_modified_context')
        if hasattr(cls, '_cls_overridden_context'):
            cls._cls_overridden_context.disable()
            delattr(cls, '_cls_overridden_context')
        super().tearDownClass()

    def __call__(self, result=None):
        """
        Wrapper around default __call__ method to perform common Django test
        set up. This means that user-defined Test Cases aren't required to
        include a call to super().setUp().
        """
        testMethod = getattr(self, self._testMethodName)
        skipped = (
            getattr(self.__class__, "__unittest_skip__", False) or
            getattr(testMethod, "__unittest_skip__", False)
        )

        if not skipped:
            try:
                self._pre_setup()
            except Exception:
                result.addError(self, sys.exc_info())
                return
        super().__call__(result)
        if not skipped:
            try:
                self._post_teardown()
            except Exception:
                result.addError(self, sys.exc_info())
                return

    def _pre_setup(self):
        """
        Perform pre-test setup:
        * Create a test client.
        * Clear the mail test outbox.
        """
        self.client = self.client_class()

    def _post_teardown(self):
        """Perform post-test things."""
        pass

    def settings(self, **kwargs):
        """
        A context manager that temporarily sets a setting and reverts to the
        original value when exiting the context.
        """
        return override_settings(**kwargs)

    def modify_settings(self, **kwargs):
        """
        A context manager that temporarily applies changes a list setting and
        reverts back to the original value when exiting the context.
        """
        return modify_settings(**kwargs)

    def assertURLEqual(self, url1, url2, msg_prefix=''):
        """
        Assert that two URLs are the same, ignoring the order of query string
        parameters except for parameters with the same name.

        For example, /path/?x=1&y=2 is equal to /path/?y=2&x=1, but
        /path/?a=1&a=2 isn't equal to /path/?a=2&a=1.
        """
        def normalize(url):
            """Sort the URL's query string parameters."""
            scheme, netloc, path, params, query, fragment = urlparse(url)
            query_parts = sorted(parse_qsl(query))
            return urlunparse((scheme, netloc, path, params, urlencode(query_parts), fragment))

        self.assertEqual(
            normalize(url1), normalize(url2),
            msg_prefix + "Expected '%s' to equal '%s'." % (url1, url2)
        )

    @contextmanager
    def _assert_raises_or_warns_cm(self, func, cm_attr, expected_exception, expected_message):
        with func(expected_exception) as cm:
            yield cm
        self.assertIn(expected_message, str(getattr(cm, cm_attr)))

    def _assertFooMessage(self, func, cm_attr, expected_exception, expected_message, *args, **kwargs):
        callable_obj = None
        if args:
            callable_obj = args[0]
            args = args[1:]
        cm = self._assert_raises_or_warns_cm(func, cm_attr, expected_exception, expected_message)
        # Assertion used in context manager fashion.
        if callable_obj is None:
            return cm
        # Assertion was passed a callable.
        with cm:
            callable_obj(*args, **kwargs)

    def assertRaisesMessage(self, expected_exception, expected_message, *args, **kwargs):
        """
        Assert that expected_message is found in the message of a raised
        exception.

        Args:
            expected_exception: Exception class expected to be raised.
            expected_message: expected error message string value.
            args: Function to be called and extra positional args.
            kwargs: Extra kwargs.
        """
        return self._assertFooMessage(
            self.assertRaises, 'exception', expected_exception, expected_message,
            *args, **kwargs
        )

    def assertWarnsMessage(self, expected_warning, expected_message, *args, **kwargs):
        """
        Same as assertRaisesMessage but for assertWarns() instead of
        assertRaises().
        """
        return self._assertFooMessage(
            self.assertWarns, 'warning', expected_warning, expected_message,
            *args, **kwargs
        )

    def assertFieldOutput(self, fieldclass, valid, invalid, field_args=None,
                          field_kwargs=None, empty_value=''):
        """
        Assert that a form field behaves correctly with various inputs.

        Args:
            fieldclass: the class of the field to be tested.
            valid: a dictionary mapping valid inputs to their expected
                    cleaned values.
            invalid: a dictionary mapping invalid inputs to one or more
                    raised error messages.
            field_args: the args passed to instantiate the field
            field_kwargs: the kwargs passed to instantiate the field
            empty_value: the expected clean output for inputs in empty_values
        """
        if field_args is None:
            field_args = []
        if field_kwargs is None:
            field_kwargs = {}
        required = fieldclass(*field_args, **field_kwargs)
        optional = fieldclass(*field_args, **{**field_kwargs, 'required': False})
        # test valid inputs
        for input, output in valid.items():
            self.assertEqual(required.clean(input), output)
            self.assertEqual(optional.clean(input), output)
        # test invalid inputs
        for input, errors in invalid.items():
            with self.assertRaises(ValidationError) as context_manager:
                required.clean(input)
            self.assertEqual(context_manager.exception.messages, errors)

            with self.assertRaises(ValidationError) as context_manager:
                optional.clean(input)
            self.assertEqual(context_manager.exception.messages, errors)
        # test required inputs
        error_required = [required.error_messages['required']]
        for e in required.empty_values:
            with self.assertRaises(ValidationError) as context_manager:
                required.clean(e)
            self.assertEqual(context_manager.exception.messages, error_required)
            self.assertEqual(optional.clean(e), empty_value)
        # test that max_length and min_length are always accepted



class TransactionTestCase(SimpleTestCase):

    # Subclasses can ask for resetting of auto increment sequence before each
    # test case
    reset_sequences = False

    # Subclasses can enable only a subset of apps for faster tests
    available_apps = None

    # Subclasses can define fixtures which will be automatically installed.
    fixtures = None

    # Do the tests in this class query non-default databases?
    multi_db = False

    # If transactions aren't available, Django will serialize the database
    # contents into a fixture during setup and flush and reload them
    # during teardown (as flush does not restore data from migrations).
    # This can be slow; this flag allows enabling on a per-case basis.
    serialized_rollback = False

    # Since tests will be wrapped in a transaction, or serialized if they
    # are not available, we allow queries to be run.
    allow_database_queries = True

    def _pre_setup(self):
        """
        Perform pre-test setup:
        * If the class has an 'available_apps' attribute, restrict the app
          registry to these applications, then fire the post_migrate signal --
          it must run with the correct set of applications for the test case.
        * If the class has a 'fixtures' attribute, install those fixtures.
        """
        super()._pre_setup()
        if self.available_apps is not None:
            apps.set_available_apps(self.available_apps)
            setting_changed.send(
                sender=settings._wrapped.__class__,
                setting='INSTALLED_APPS',
                value=self.available_apps,
                enter=True,
            )
            for db_name in self._databases_names(include_mirrors=False):
                emit_post_migrate_signal(verbosity=0, interactive=False, db=db_name)
        try:
            self._fixture_setup()
        except Exception:
            if self.available_apps is not None:
                apps.unset_available_apps()
                setting_changed.send(
                    sender=settings._wrapped.__class__,
                    setting='INSTALLED_APPS',
                    value=settings.INSTALLED_APPS,
                    enter=False,
                )
            raise
        # Clear the queries_log so that it's less likely to overflow (a single
        # test probably won't execute 9K queries). If queries_log overflows,
        # then assertNumQueries() doesn't work.
        for db_name in self._databases_names(include_mirrors=False):
            connections[db_name].queries_log.clear()

    @classmethod
    def _databases_names(cls, include_mirrors=True):
        # If the test case has a multi_db=True flag, act on all databases,
        # including mirrors or not. Otherwise, just on the default DB.
        if cls.multi_db:
            return [
                alias for alias in connections
                if include_mirrors or not connections[alias].settings_dict['TEST']['MIRROR']
            ]
        else:
            return [DEFAULT_DB_ALIAS]

    def _reset_sequences(self, db_name):
        conn = connections[db_name]
        if conn.features.supports_sequence_reset:
            sql_list = conn.ops.sequence_reset_by_name_sql(
                no_style(), conn.introspection.sequence_list())
            if sql_list:
                with transaction.atomic(using=db_name):
                    with conn.cursor() as cursor:
                        for sql in sql_list:
                            cursor.execute(sql)

    def _fixture_setup(self):
        for db_name in self._databases_names(include_mirrors=False):
            # Reset sequences
            if self.reset_sequences:
                self._reset_sequences(db_name)

            # If we need to provide replica initial data from migrated apps,
            # then do so.
            if self.serialized_rollback and hasattr(connections[db_name], "_test_serialized_contents"):
                if self.available_apps is not None:
                    apps.unset_available_apps()
                connections[db_name].creation.deserialize_db_from_string(
                    connections[db_name]._test_serialized_contents
                )
                if self.available_apps is not None:
                    apps.set_available_apps(self.available_apps)

            if self.fixtures:
                # We have to use this slightly awkward syntax due to the fact
                # that we're using *args and **kwargs together.
                call_command('loaddata', *self.fixtures,
                             **{'verbosity': 0, 'database': db_name})

    def _should_reload_connections(self):
        return True

    def _post_teardown(self):
        """
        Perform post-test things:
        * Flush the contents of the database to leave a clean slate. If the
          class has an 'available_apps' attribute, don't fire post_migrate.
        * Force-close the connection so the next test gets a clean cursor.
        """
        try:
            self._fixture_teardown()
            super()._post_teardown()
            if self._should_reload_connections():
                # Some DB cursors include SQL statements as part of cursor
                # creation. If you have a test that does a rollback, the effect
                # of these statements is lost, which can affect the operation of
                # tests (e.g., losing a timezone setting causing objects to be
                # created with the wrong time). To make sure this doesn't
                # happen, get a clean connection at the start of every test.
                for conn in connections.all():
                    conn.close()
        finally:
            if self.available_apps is not None:
                apps.unset_available_apps()
                setting_changed.send(sender=settings._wrapped.__class__,
                                     setting='INSTALLED_APPS',
                                     value=settings.INSTALLED_APPS,
                                     enter=False)

    def _fixture_teardown(self):
        # Allow TRUNCATE ... CASCADE and don't emit the post_migrate signal
        # when flushing only a subset of the apps
        for db_name in self._databases_names(include_mirrors=False):
            # Flush the database
            inhibit_post_migrate = (
                self.available_apps is not None or
                (   # Inhibit the post_migrate signal when using serialized
                    # rollback to avoid trying to recreate the serialized data.
                    self.serialized_rollback and
                    hasattr(connections[db_name], '_test_serialized_contents')
                )
            )
            call_command('flush', verbosity=0, interactive=False,
                         database=db_name, reset_sequences=False,
                         allow_cascade=self.available_apps is not None,
                         inhibit_post_migrate=inhibit_post_migrate)

    def assertQuerysetEqual(self, qs, values, transform=repr, ordered=True, msg=None):
        items = map(transform, qs)
        if not ordered:
            return self.assertEqual(Counter(items), Counter(values), msg=msg)
        values = list(values)
        # For example qs.iterator() could be passed as qs, but it does not
        # have 'ordered' attribute.
        if len(values) > 1 and hasattr(qs, 'ordered') and not qs.ordered:
            raise ValueError("Trying to compare non-ordered queryset "
                             "against more than one ordered values")
        return self.assertEqual(list(items), values, msg=msg)

    def assertNumQueries(self, num, func=None, *args, using=DEFAULT_DB_ALIAS, **kwargs):
        conn = connections[using]

        context = _AssertNumQueriesContext(self, num, conn)
        if func is None:
            return context

        with context:
            func(*args, **kwargs)


def connections_support_transactions():
    """Return True if all connections support transactions."""
    return all(conn.features.supports_transactions for conn in connections.all())


class TestCase(TransactionTestCase):
    """
    Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
    test isolation.

    In most situations, TestCase should be preferred to TransactionTestCase as
    it allows faster execution. However, there are some situations where using
    TransactionTestCase might be necessary (e.g. testing some transactional
    behavior).

    On database backends with no transaction support, TestCase behaves as
    TransactionTestCase.
    """
    @classmethod
    def _enter_atomics(cls):
        """Open atomic blocks for multiple databases."""
        atomics = {}
        for db_name in cls._databases_names():
            atomics[db_name] = transaction.atomic(using=db_name)
            atomics[db_name].__enter__()
        return atomics

    @classmethod
    def _rollback_atomics(cls, atomics):
        """Rollback atomic blocks opened by the previous method."""
        for db_name in reversed(cls._databases_names()):
            transaction.set_rollback(True, using=db_name)
            atomics[db_name].__exit__(None, None, None)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not connections_support_transactions():
            return
        cls.cls_atomics = cls._enter_atomics()

        if cls.fixtures:
            for db_name in cls._databases_names(include_mirrors=False):
                try:
                    call_command('loaddata', *cls.fixtures, **{'verbosity': 0, 'database': db_name})
                except Exception:
                    cls._rollback_atomics(cls.cls_atomics)
                    raise
        try:
            cls.setUpTestData()
        except Exception:
            cls._rollback_atomics(cls.cls_atomics)
            raise

    @classmethod
    def tearDownClass(cls):
        if connections_support_transactions():
            cls._rollback_atomics(cls.cls_atomics)
            for conn in connections.all():
                conn.close()
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        """Load initial data for the TestCase."""
        pass

    def _should_reload_connections(self):
        if connections_support_transactions():
            return False
        return super()._should_reload_connections()

    def _fixture_setup(self):
        if not connections_support_transactions():
            # If the backend does not support transactions, we should reload
            # class data before each test
            self.setUpTestData()
            return super()._fixture_setup()

        assert not self.reset_sequences, 'reset_sequences cannot be used on TestCase instances'
        self.atomics = self._enter_atomics()

    def _fixture_teardown(self):
        if not connections_support_transactions():
            return super()._fixture_teardown()
        try:
            for db_name in reversed(self._databases_names()):
                if self._should_check_constraints(connections[db_name]):
                    connections[db_name].check_constraints()
        finally:
            self._rollback_atomics(self.atomics)

    def _should_check_constraints(self, connection):
        return (
            connection.features.can_defer_constraint_checks and
            not connection.needs_rollback and connection.is_usable()
        )


class CheckCondition:
    """Descriptor class for deferred condition checking."""
    def __init__(self, *conditions):
        self.conditions = conditions

    def add_condition(self, condition, reason):
        return self.__class__(*self.conditions, (condition, reason))

    def __get__(self, instance, cls=None):
        # Trigger access for all bases.
        if any(getattr(base, '__unittest_skip__', False) for base in cls.__bases__):
            return True
        for condition, reason in self.conditions:
            if condition():
                # Override this descriptor's value and set the skip reason.
                cls.__unittest_skip__ = True
                cls.__unittest_skip_why__ = reason
                return True
        return False


def _deferredSkip(condition, reason):
    def decorator(test_func):
        if not (isinstance(test_func, type) and
                issubclass(test_func, unittest.TestCase)):
            @wraps(test_func)
            def skip_wrapper(*args, **kwargs):
                if condition():
                    raise unittest.SkipTest(reason)
                return test_func(*args, **kwargs)
            test_item = skip_wrapper
        else:
            # Assume a class is decorated
            test_item = test_func
            # Retrieve the possibly existing value from the class's dict to
            # avoid triggering the descriptor.
            skip = test_func.__dict__.get('__unittest_skip__')
            if isinstance(skip, CheckCondition):
                test_item.__unittest_skip__ = skip.add_condition(condition, reason)
            elif skip is not True:
                test_item.__unittest_skip__ = CheckCondition((condition, reason))
        return test_item
    return decorator


def skipIfDBFeature(*features):
    """Skip a test if a database has at least one of the named features."""
    return _deferredSkip(
        lambda: any(getattr(connection.features, feature, False) for feature in features),
        "Database has feature(s) %s" % ", ".join(features)
    )


def skipUnlessDBFeature(*features):
    """Skip a test unless a database has all the named features."""
    return _deferredSkip(
        lambda: not all(getattr(connection.features, feature, False) for feature in features),
        "Database doesn't support feature(s): %s" % ", ".join(features)
    )


def skipUnlessAnyDBFeature(*features):
    """Skip a test unless a database has any of the named features."""
    return _deferredSkip(
        lambda: not any(getattr(connection.features, feature, False) for feature in features),
        "Database doesn't support any of the feature(s): %s" % ", ".join(features)
    )


class SerializeMixin:
    """
    Enforce serialization of TestCases that share a common resource.

    Define a common 'lockfile' for each set of TestCases to serialize. This
    file must exist on the filesystem.

    Place it early in the MRO in order to isolate setUpClass()/tearDownClass().
    """
    lockfile = None

    @classmethod
    def setUpClass(cls):
        if cls.lockfile is None:
            raise ValueError(
                "{}.lockfile isn't set. Set it to a unique value "
                "in the base class.".format(cls.__name__))
        cls._lockfile = open(cls.lockfile)
        locks.lock(cls._lockfile, locks.LOCK_EX)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._lockfile.close()
