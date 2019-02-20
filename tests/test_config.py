import os
import tempfile
import unittest

from yesaide import config


class AbstractTestConfig(object):
    def test_common(self):
        self.assertEqual(self.a_config["KEY_ONE"], "blaé")

        with self.assertRaises(config.ConfigError):
            self.a_config["key_three"]

        with self.assertRaises(config.ConfigError):
            self.a_config["KEY_FOUR"]

    def test_dict_interface(self):
        self.assertEqual(self.a_config["KEY_ONE"], "blaé")
        self.assertEqual(self.a_config.get("KEY_ONE"), "blaé")
        self.assertEqual(self.a_config.get("KEY_THREE", "no"), "no")
        self.assertEqual(self.a_config.get("KEY_FOUR"), None)

    def test_with_integer(self):
        self.assertEqual(self.a_config["KEY_TWO"], 12)

    def tearDown(self):
        del self.a_config


class TestObjectConfig(unittest.TestCase, AbstractTestConfig):
    def setUp(self):
        class DummyObject(object):
            pass

        test_object = DummyObject()
        setattr(test_object, "KEY_ONE", "blaé")
        setattr(test_object, "KEY_TWO", 12)
        setattr(test_object, "key_three", "non_capital")

        self.a_config = config.Config()
        self.a_config.from_object(test_object)


class TestFileConfig(unittest.TestCase, AbstractTestConfig):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(mode="w", delete=False)

        self.test_file.write('KEY_ONE = "blaé"\n')
        self.test_file.write("KEY_TWO = 12\n")
        self.test_file.write('key_three = "non_capital"\n')

        self.test_file.close()

        self.a_config = config.Config()
        self.a_config.from_pyfile(self.test_file.name)

    def tearDown(self):
        del self.a_config
        os.remove(self.test_file.name)
        del self.test_file


class TestManualConfig(unittest.TestCase, AbstractTestConfig):
    def setUp(self):
        self.a_config = config.Config()

        self.a_config["KEY_ONE"] = "blaé"
        self.a_config["KEY_TWO"] = 12


class TestEnvConfig(unittest.TestCase, AbstractTestConfig):
    def setUp(self):
        os.environ["OH_KEY_ONE"] = "blaé"

        self.a_config = config.Config(env_prefix="OH_")

    def test_with_integer(self):
        pass


class TestDefaultConfigRequired(unittest.TestCase, AbstractTestConfig):
    def setUp(self):
        class DummyObject(object):
            pass

        test_object = DummyObject()
        setattr(test_object, "KEY_ONE", "blaé")
        setattr(test_object, "KEY_TWO", 12)
        setattr(test_object, "key_three", "non_capital")
        setattr(test_object, "KEY_FIVE", config.Required())

        self.a_config = config.Config(default_config=test_object)

    def test_required_values(self):
        self.assertFalse(self.a_config.is_valid())
        self.assertTrue(["KEY_FIVE"] == self.a_config.missing_values())

        self.a_config["KEY_FIVE"] = "foo"

        self.assertTrue(self.a_config.is_valid())
