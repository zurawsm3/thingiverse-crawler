# -*- coding: utf-8 -*-
import psycopg2


class ThingiverseProPipeline(object):

    def process_item(self, item, spider):
        return item

    def open_spider(self, spider):
        """
            PARAMETRY BAZY DANYCH
        """
        hostname = 'db'
        username = 'postgres'
        password = 'postgres123'  # your password
        database = 'things'
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS things_table("
                         "number_of_thing serial PRIMARY KEY, "
                         "author VARCHAR,"
                         "title VARCHAR, "
                         "likes VARCHAR,"
                         "date_thing VARCHAR,"
                         "downloads VARCHAR,"
                         "views VARCHAR,"
                         "license VARCHAR(100));")

        self.cur.execute("CREATE TABLE IF NOT EXISTS makes ("
                         "id_make serial PRIMARY KEY,"
                         "num_of_make VARCHAR, "
                         "id_thing INTEGER REFERENCES things_table(number_of_thing));")

        self.cur.execute("CREATE TABLE IF NOT EXISTS remixes ("
                         "id_remix serial PRIMARY KEY, "
                         "num_of_remix VARCHAR, "
                         "id_thing INTEGER REFERENCES things_table(number_of_thing));")

        self.cur.execute("CREATE TABLE IF NOT EXISTS description ("
                         "id_desc serial PRIMARY KEY, "
                         "title_desc VARCHAR, "
                         "cont_desc VARCHAR, "
                         "id_thing INTEGER REFERENCES things_table(number_of_thing));")

        self.cur.execute("CREATE TABLE IF NOT EXISTS tags ("
                         "id_tag serial PRIMARY KEY, "
                         "tag_name VARCHAR, "
                         "id_thing INTEGER REFERENCES things_table(number_of_thing));")

        self.cur.execute("CREATE TABLE IF NOT EXISTS comments ("
                         "id_comm serial PRIMARY KEY, "
                         "id_container  VARCHAR, "
                         "comm_content VARCHAR, "
                         "papa_id VARCHAR, "
                         "comm_author VARCHAR, "
                         "comm_date VARCHAR, "
                         "id_thing INTEGER REFERENCES things_table(number_of_thing));")

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):

        self.cur.execute(
            "INSERT INTO things_table ("
            "number_of_thing, "
            " author, "
            "title, "
            "likes, "
            "date_thing, "
            "downloads, "
            "views, "
            "license) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;",
            (item['num_thing'][0],
             item['author'][0],
             item['title'][0].strip(),
             item['like'][0],
             item['date_thing'][0],
             item['downloads'][0],
             item['views'][0],
             item['license'][0]))

        for i in item['remixes']:
            self.cur.execute(
                "INSERT INTO remixes ("
                "num_of_remix, id_thing) "
                "VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (i, item['num_thing'][0]))

        for p in item['makes']:
            self.cur.execute(
                "INSERT INTO makes ("
                "num_of_make, id_thing) "
                "VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (p, item['num_thing'][0]))

        for i, x in zip(item['desc_title'], item['desc_cont']):
            self.cur.execute(
                "INSERT INTO description ("
                "title_desc, cont_desc, id_thing) "
                "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                (i, x, item['num_thing'][0]))

        for i, k, x, n, m in zip(
                item['comm'][0]['id_container'],
                item['comm'][0]['comm_content'],
                item['comm'][0]['papa_id'],
                item['comm'][0]['comm_author'],
                item['comm'][0]['comm_date']):
            self.cur.execute(
                "INSERT INTO comments ("
                "id_container, comm_content, papa_id, comm_author, comm_date, id_thing) "
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;",
                (i, k, x, n, m, item['num_thing'][0]))

        for i in item['tags']:
            self.cur.execute("INSERT INTO tags (tag_name, id_thing) values (%s, %s) ON CONFLICT DO NOTHING;", (i, item['num_thing'][0]))
        self.connection.commit()


