import sqlite3
from lib import CONN, CURSOR  # Import connection and cursor from your environment setup

class Review:
    all = {}  # Dictionary to cache instances by their primary key (id)

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review id={self.id}, year={self.year}, summary='{self.summary}', employee_id={self.employee_id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER NOT NULL,
                summary TEXT NOT NULL,
                employee_id INTEGER,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute('DROP TABLE IF EXISTS reviews')
        CONN.commit()

    def save(self):
        """Save instance to the database and cache it."""
        CURSOR.execute('''
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        ''', (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        self.__class__.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create a new Review instance and save it to the database."""
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance from a database row, using cache if available."""
        id = row[0]
        if id in cls.all:
            instance = cls.all[id]
            instance.year, instance.summary, instance.employee_id = row[1:]
        else:
            instance = cls(*row)
            cls.all[id] = instance
        return instance

    @classmethod
    def find_by_id(cls, id):
        """Find a Review by id."""
        CURSOR.execute('SELECT * FROM reviews WHERE id = ?', (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        """Update the Review row in the database based on the current instance."""
        CURSOR.execute('''
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        ''', (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the Review row from the database and remove from cache."""
        CURSOR.execute('DELETE FROM reviews WHERE id = ?', (self.id,))
        CONN.commit()
        if self.id in self.__class__.all:
            del self.__class__.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances in the database."""
        CURSOR.execute('SELECT * FROM reviews')
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property methods for validation
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000.")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value:
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string.")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if isinstance(value, int) and self._validate_employee_id(value):
            self._employee_id = value
        else:
            raise ValueError("employee_id must be the ID of a valid Employee.")

    @staticmethod
    def _validate_employee_id(employee_id):
        """Check if the employee_id exists in the 'employees' table."""
        CURSOR.execute('SELECT id FROM employees WHERE id = ?', (employee_id,))
        return CURSOR.fetchone() is not None


