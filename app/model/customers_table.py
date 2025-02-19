from flask import abort
import sqlite3
from model.database import get_db


class CustomersTable:

    @staticmethod
    def get():
        """Gets all rows from the customers table.

            If the database operations raise a sqlite3.Error, the method is 
            aborted with the status code 500.

        Returns:
            list: a list of all rows; each row is a dictionary that maps
                column names to values. An empty list is returned if the 
                table has no columns.
        """
        try:
            db = get_db()
            result = db.execute("SELECT * FROM CUSTOMERS ORDER BY LastName")
            customers = result.fetchall()
            customers = [dict(customer) for customer in customers]
            return customers
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)
