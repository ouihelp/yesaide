import unittest

from yesaide import database, worker


class TestDatabase(unittest.TestCase):
    class FakeDbSession(object):
        def __init__(self):
            self.has_been_committed = False

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
        # Default is to auto commit.
        self.assertTrue(self.dbsession.has_been_committed)

    def test_db_method_with_commit_true(self):
        self.worker.fake_method(commit=True)
        self.assertTrue(self.dbsession.has_been_committed)

    def test_db_method_with_commit_false(self):
        self.worker.fake_method(commit=False)
        self.assertTrue(not self.dbsession.has_been_committed)
