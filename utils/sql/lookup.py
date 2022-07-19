import sqlite3

class SQLDatabase:
    """
    This class represents a connection to a SQLite3 database.
    """
    def __init__(self, db_name=None, table_name=None, column_name=None):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.connection.enable_load_extension(True)
        self.connection.load_extension('dbs/spellfix')
        self.connection.enable_load_extension(False)
        self.cursor = self.connection.cursor()


class SQLiteQuery:
    """
    This class is used to look up various info in the databases.
    """
    def __init__(self, word=None, lookup_type=None, table_name=None, cursor=None, original=None, correction=None):
        self.word = word
        self.lookup_type = lookup_type
        self.cursor = cursor
        self.table_name = table_name
        self.exists = self._exists
        self.corrections = self.get_correction_of_error

    def _exists(self):
        """
        This method is intended to be used with the databases and
        returns True if a word form or a lemma exists in the
        database. Else it returns False.
        """
        self.cursor.execute(f"""
                                SELECT 1
                                FROM {self.table_name}
                                WHERE {self.lookup_type} = ?
                            """, (self.word,))
        return True if self.cursor.fetchone() else False


    def get_correction_of_error(self):
        """
        Returns all possible substitutions of a given string (emi -> erni/enni)
        """
        self.cursor.execute(f"""
                                SELECT correction
                                FROM {self.table_name}
                                WHERE original = ?
                                ORDER BY frequency DESC
                            """, (self.word,))
        return self.cursor.fetchall()

    def get_freq_of_item(self, item):
        self.cursor.execute(f"""
                                SELECT frequency
                                from {self.table_name}
                                WHERE {self.lookup_type} = ?
                            """, (item,))
        return self.cursor.fetchone()

    def get_replacements_by_original(self, original_ngr, freq):
        self.cursor.execute(f"""
                                SELECT replacement, frequency
                                FROM {self.table_name}
                                WHERE original = ? and frequency > {freq}
                                ORDER BY frequency DESC
                            """, (original_ngr,))
        return self.cursor.fetchall()

    def get_replacement_by_corrected(self, corrected_ngr, freq):
        self.cursor.execute(f"""
                                SELECT original, frequency
                                FROM {self.table_name}
                                WHERE replacement = ? and frequency > {freq}
                                ORDER BY frequency DESC
                            """, (corrected_ngr,))
        return self.cursor.fetchall()

    def get_similar(self, word, edit_cost, column):
        self.cursor.execute(f"""
                                SELECT {column}
                                FROM {self.table_name}
                                WHERE editdist3(?, {column}) < {edit_cost}
                            """, (word,))
        return self.cursor.fetchall()

    def get_similar_and_frequency(self, word, edit_cost, column, tok_freq=0):
        self.cursor.execute(f"""
                                SELECT {column}, frequency
                                FROM {self.table_name}
                                WHERE editdist3(?, {column}) < {edit_cost}
                                AND frequency > {tok_freq}
                            """, (word,))
        return self.cursor.fetchall()

    def get_col_sum(self, column):
        self.cursor.execute(f"""
                                SELECT SUM({column})
                                FROM {self.table_name}
                            """)
        return self.cursor.fetchone()[0]

if __name__ == '__main__':
    pass
