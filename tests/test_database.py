import unittest

from yesaide import database, worker


class TestDatabase(unittest.TestCase):
    class FakeDbSession(object):
        def __init__(self):
            self.has_been_committed = False
            self.has_been_flushed = False

        def flush(self):
            self.has_been_flushed = True

        def commit(self):
            self.has_been_committed = True

    class TestedWorker(worker.RawWorker):
        @database.db_method
        def fake_method(self):
            pass

    def setUp(self):
        self.dbsession = self.FakeDbSession()
        self.worker = self.TestedWorker(self.dbsession)

    def tearDown(self):
        del self.dbsession
        del self.worker

    def test_db_method(self):
        self.worker.fake_method()
        # Default is to auto commit and no flush
        self.assertTrue(self.dbsession.has_been_committed)
        self.assertFalse(self.dbsession.has_been_flushed)

    def test_db_method_no_simultaneaous_commit_and_flush(self):
        self.worker.fake_method()
        # Raises if flush and commit are both True
        self.assertRaises(Exception)

    def test_db_method_with_commit_true(self):
        self.worker.fake_method(commit=True)
        self.assertTrue(self.dbsession.has_been_committed)

    def test_db_method_with_commit_false(self):
        self.worker.fake_method(commit=False)
        self.assertFalse(self.dbsession.has_been_committed)

    def test_db_method_with_flush_true(self):
        self.worker.fake_method(flush=True, commit=False)
        self.assertTrue(self.dbsession.has_been_flushed)

    def test_db_method_with_flush_false(self):
        self.worker.fake_method(flush=False)
        self.assertFalse(self.dbsession.has_been_flushed)
