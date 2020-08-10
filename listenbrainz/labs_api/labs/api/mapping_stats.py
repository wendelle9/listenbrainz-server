#!/usr/bin/env python3

import psycopg2
import psycopg2.extras
from datasethoster import Query
from datasethoster.main import register_query
from flask import current_app


class MSBMappingStatsQuery(Query):

    def names(self):
        return ("mapping-stats", "Fetch stats about the recent MSB mappings that were generated.")

    def inputs(self):
        return []

    def introduction(self):
        return """This page allows you to look at the stats for recently generated MSB mappings."""

    def outputs(self):
        return ['stats']

    def fetch(self, params, offset=-1, count=-1):

        with psycopg2.connect(current_app.config['DB_CONNECT_MAPPING']) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
                query = """SELECT stats FROM mapping.stats"""
                args = [msid]
                if count > 0:
                    query += " LIMIT %s"
                    args.append(count)
                if offset >= 0:
                    query += " OFFSET %s"
                    args.append(offset)

                curs.execute(query)
                results = []
                while True:
                    row = curs.fetchone()
                    if not row:
                        break

                    results.append(dict(row))

                return results
