import pandas as pd
import sqlite3
import csv

class FileToSQL:
    def __init__(self, file_to_db=None, db_name=None, include_index=True):
        self.file_to_db = file_to_db
        self.db_name = db_name
        self.include_index = include_index
        self.connection = sqlite3.connect(f'{self.db_name}.db')

    def create_lookup_datasbase(self, table_name, column_name, field_separator, headers):
        self.connection.execute(f"""CREATE TABLE
                                if not exists {table_name}
                                ({column_name} TEXT)""")
        if self.include_index:
            self.connection.execute(f"""CREATE INDEX word_form_id
                                    ON {table_name} ({column_name})""")

        data = pd.read_csv(self.file_to_db, sep=field_separator, dtype=str, names=headers, quoting=csv.QUOTE_NONE)
        df = pd.DataFrame(data, columns=[column_name])
        df.drop_duplicates(subset=None, keep='first', inplace=True)
        df.to_sql(f'{table_name}', self.connection, if_exists='append', index=False)

    def create_relational_database(self, table_name, column1, column2, headers, field_separator=';'):
        self.connection.execute(f"""CREATE TABLE
                                    if not exists {table_name}
                                    ({column1} TEXT)""")

        self.connection.execute(f"""ALTER TABLE
                                   {table_name}
                                    ADD COLUMN {column2} INTEGER""")
        if self.include_index:
            self.connection.execute(f""" CREATE INDEX lemma_index
                                    ON {table_name} ({column1})
                                    """)
            self.connection.execute(f""" CREATE INDEX word_form_index
                                    ON {table_name} ({column2})
                                    """)


        data = pd.read_csv(self.file_to_db, sep=field_separator, dtype=str, names=headers, quoting=csv.QUOTE_NONE)
        df = pd.DataFrame(data, columns=[column1, column2])
        df.to_sql(f'{table_name}', self.connection, if_exists='append', index=False)

    def create_freq_lookup_db(self, table_name, column1, column2, headers, field_separator='\t'):
        self.connection.execute(f"""CREATE TABLE
                                    if not exists {table_name}
                                    ({column1} TEXT)""")

        self.connection.execute(f"""ALTER TABLE
                                   {table_name}
                                    ADD COLUMN {column2} INTEGER""")
        if self.include_index:
            self.connection.execute(f""" CREATE INDEX lemma_index
                                    ON {table_name} ({column1})
                                    """)
            self.connection.execute(f""" CREATE INDEX word_form_index
                                    ON {table_name} ({column2})
                                    """)


        data = pd.read_csv(self.file_to_db, sep=field_separator, dtype=str, names=headers, quoting=csv.QUOTE_NONE)
        df = pd.DataFrame(data, columns=[column1, column2])
        df = df.replace(to_replace='None', value='<unk>').dropna()
        df.to_sql(f'{table_name}', self.connection, if_exists='append', index=False)

    def create_db_orig_corr_freq(self, table_name, column1, column2, column3, headers, field_separator=';'):
        self.connection.execute(f"""CREATE TABLE
                                    if not exists {table_name}
                                    ({column1} TEXT)""")

        self.connection.execute(f"""ALTER TABLE
                                   {table_name}
                                    ADD COLUMN {column2} TEXT""")

        self.connection.execute(f"""ALTER TABLE
                                   {table_name}
                                    ADD COLUMN {column3} INTEGER""")

        if self.include_index:
            self.connection.execute(f""" CREATE INDEX column_one_index
                                    ON {table_name} ({column1})
                                    """)
            self.connection.execute(f""" CREATE INDEX column_two_index
                                    ON {table_name} ({column2})
                                    """)
            self.connection.execute(f""" CREATE INDEX column_three_index
                                    ON {table_name} ({column3})
                                    """)


        data = pd.read_csv(self.file_to_db, sep=field_separator, dtype=str, names=headers, quoting=csv.QUOTE_NONE)
        df = pd.DataFrame(data, columns=[column1, column2, column3])
        df.to_sql(f'{table_name}', self.connection, if_exists='append', index=False)

if __name__ == '__main__':
    pass