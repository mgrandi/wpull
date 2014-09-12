# encoding=utf-8


import unittest

from wpull.database.sqltable import SQLiteURLTable
from wpull.item import Status


class TestDatabase(unittest.TestCase):
    def test_sqlite_url_table(self):
        url_table = SQLiteURLTable(':memory:')
        self._generic_url_table_tester(url_table)

    def _generic_url_table_tester(self, url_table):
        urls = [
            'http://example.com',
            'http://example.com/kitteh',
            'http://example.com/doge',
        ]
        url_table.add_many(
            urls, referrer='http://example.com', level=0,
            top_url='http://example.net',
        )

        self.assertTrue(url_table.contains(urls[0]))
        self.assertTrue(url_table.contains(urls[1]))
        self.assertTrue(url_table.contains(urls[2]))
        self.assertEqual(3, url_table.count())

        for i in range(3):
            url_record = url_table.get_one(urls[i])

            self.assertEqual(urls[i], url_record.url)
            self.assertEqual(Status.todo, url_record.status)
            self.assertEqual(0, url_record.try_count)
            self.assertEqual('http://example.com', url_record.referrer)
            self.assertEqual('http://example.net', url_record.top_url)

        url_record = url_table.check_out(
            Status.todo,
        )

        self.assertEqual(Status.in_progress, url_record.status)

        url_table.check_in(url_record.url, Status.done,
                           increment_try_count=True, status_code=200)

        url_record = url_table.get_one(url_record.url)

        self.assertEqual(200, url_record.status_code)
        self.assertEqual(Status.done, url_record.status)
        self.assertEqual(1, url_record.try_count)

        url_record_dict = url_record.to_dict()
        self.assertEqual(200, url_record_dict['status_code'])
        self.assertEqual(Status.done, url_record_dict['status'])
        self.assertEqual(1, url_record_dict['try_count'])

        self.assertFalse(
            url_table.get_revisit_id('http://example.com/1', 'digest123')
        )

        url_table.add_visits([
            ('http://example.com/1', 'id123', 'digest123'),
            ('http://example.com/2', 'id456', 'digest456'),
        ])

        self.assertEqual(
            'id123',
            url_table.get_revisit_id('http://example.com/1', 'digest123')
        )
        self.assertEqual(
            'id456',
            url_table.get_revisit_id('http://example.com/2', 'digest456')
        )
        self.assertFalse(
            url_table.get_revisit_id('http://example.com/1', 'digestbad')
        )
        self.assertFalse(
            url_table.get_revisit_id('http://example.com/2', 'digestbad')
        )
        self.assertFalse(
            url_table.get_revisit_id('http://example.com/asdf', 'digest123')
        )