from yesaide import worker

import test_worker


class InvalidWorker(worker.MappingManagingWorker):
    pass


class Worker(worker.MappingManagingWorker):
    def serialize(self, item):
        return {"a_prop": item.a_prop}


class TestInvalidWorker(test_worker.BaseTestWorker):
    def test_invalid_worker(self):
        foreman = test_worker.FakeForeman()
        a_worker = InvalidWorker(
            foreman, managed_sqla_map=test_worker.FakeMapping, managed_sqla_map_name="fake"
        )

        with self.assertRaises(NotImplementedError):
            a_worker.serialize(test_worker.FakeMapping())


class TestSerialize(test_worker.BaseTestWorker):
    def setUp(self):
        foreman = test_worker.FakeForeman()
        self.a_worker = Worker(
            foreman, managed_sqla_map=test_worker.FakeMapping, managed_sqla_map_name="fake"
        )
        test_worker.BaseTestWorker.setUp(self)

    def tearDown(self):
        del self.a_worker
        test_worker.BaseTestWorker.tearDown(self)

    def test_serialize(self):
        fake_item = test_worker.FakeMapping()
        serialized = self.a_worker.serialize(fake_item)

        self.assertTrue(isinstance(serialized, dict))
        self.assertEqual(serialized["a_prop"], fake_item.a_prop)
