# -*- coding: utf-8 -*-
import unittest

from voluptuous import Schema, MultipleInvalid, Required

from zombase import validation


class TestEmail(unittest.TestCase):

    def test_email(self):
        schema = Schema(validation.Email())
        schema('a@b.cc')

    def test_other_email(self):
        schema = Schema(validation.Email())
        schema('a+d@b.cc')

    def test_lower_email(self):
        schema = Schema(validation.Email())
        schema_lower = Schema(validation.Email(lower=True))

        self.assertEqual(schema('aZ@b.cc'), 'aZ@b.cc')
        self.assertEqual(schema_lower('aZ@b.cc'), 'az@b.cc')

    def test_invalid_email(self):
        schema = Schema(validation.Email())

        with self.assertRaises(MultipleInvalid):
            schema('a a@b.c')


class TestFloatable(unittest.TestCase):

    def test_simple_floatable(self):
        schema = Schema(validation.Floatable())
        self.assertEqual(schema('1.12'), 1.12)
        self.assertEqual(schema(1.12), 1.12)

    def test_empty_to_none_floatable(self):
        schema = Schema(validation.Floatable(empty_to_none=True))
        self.assertEqual(schema(''), None)

    def test_uncasted_floatable(self):
        schema = Schema(validation.Floatable(cast=False))
        self.assertEqual(schema('3.0'), '3.0')

    def test_invalid_floatable(self):
        schema = Schema(validation.Floatable())
        with self.assertRaises(MultipleInvalid):
            schema('3.a')


class TestIntegeable(unittest.TestCase):

    def test_simple_integeable(self):
        schema = Schema(validation.Integeable())
        self.assertEqual(schema('1'), 1)

    def test_empty_to_none_integeable(self):
        schema = Schema(validation.Integeable(empty_to_none=True))
        self.assertEqual(schema(''), None)

    def test_uncasted_integeable(self):
        schema = Schema(validation.Integeable(cast=False))
        self.assertEqual(schema('3'), '3')

    def test_invalid_integeable(self):
        schema = Schema(validation.Integeable())
        with self.assertRaises(MultipleInvalid):
            schema('a')

    def test_invalid_integeable_but_floatable(self):
        schema = Schema(validation.Integeable())

        with self.assertRaises(MultipleInvalid):
            schema('3.2')

        with self.assertRaises(MultipleInvalid):
            schema(3.2)


class TestChoice(unittest.TestCase):

    def test_choice(self):
        schema = Schema(validation.Choice(['a', 'b']))
        schema('a')

    def test_wrong_choice(self):
        schema = Schema(validation.Choice(['a', 'b']))
        with self.assertRaises(MultipleInvalid):
            schema('c')

    def test_wrong_choice_in_dict(self):
        # The error message system is different in a dict.
        schema = Schema({
            'bla': validation.Choice(['a', 'b']),
        })
        with self.assertRaises(MultipleInvalid):
            schema({'bla': 'c'})


class TestAdaptDict(unittest.TestCase):

    input_dict = {
        'to_keep': 'dummy',
        'to_remove': 'dummy',
        'to_make_required': 'dummy'
    }

    def test_keep(self):
        output_dict = validation.adapt_dict(self.input_dict, keep=['to_keep'])
        self.assertEqual(output_dict, {'to_keep': 'dummy'})

    def test_remove(self):
        output_dict = validation.adapt_dict(
            self.input_dict, remove=['to_remove'])
        self.assertEqual(output_dict, {'to_keep': 'dummy',
                                       'to_make_required': 'dummy'})

    def test_make_required(self):
        output_dict = validation.adapt_dict(
            self.input_dict, make_required=['to_make_required'])

        def the_assert(output_dict):
            for key in output_dict:
                if (str(key) == 'to_make_required'
                        and not isinstance(key, Required)):
                    return False
                elif (str(key) != 'to_make_required'
                        and isinstance(key, Required)):
                    return False
            return True
        self.assertTrue(the_assert(output_dict))


class TestSchemaDictNone(unittest.TestCase):

    schema_dict = {
        Required('id'): int,
        'name': str,
        'value': int,
        'target': int,
    }

    def test_wrong_init(self):
        with self.assertRaises(ValueError):
            validation.SchemaDictNone(['a', 'b'])

    def test_basic_schema(self):
        schema = validation.SchemaDictNone(self.schema_dict)

        data = {'id': 2, 'name': 'bla', 'value': None}
        new_data = schema(data)

        self.assertEqual(new_data['value'], None)
        self.assertEqual(new_data['name'], 'bla')

    def test_schema_with_not_none(self):
        schema = validation.SchemaDictNone(
            self.schema_dict, not_none=('name',))

        data = {'id': 2, 'value': None, 'name': None}

        with self.assertRaises(MultipleInvalid):
            schema(data)
