from flask import abort
import sqlite3
from model.database import get_db


class CategoriesTable:

    @staticmethod
    def get():
        """Gets all rows from the categories table.

            If the database operations raise a sqlite3.Error, the method is 
            aborted with the status code 500.

        Returns:
            list: a list of all rows; each row is a dictionary that maps
                column names to values. An empty list is returned if the 
                table has no columns.
        """
        try:
            db = get_db()
            result = db.execute("SELECT * FROM CATEGORIES")
            categories = result.fetchall()
            categories = [dict(category) for category in categories]
            return categories
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)


    @staticmethod
    def get_by_id(category_id):
        """Gets the row with the specified id from the categories table
            
            If the database operations raise a sqlite3.Error, the method is 
            aborted with the status code 500.

        Args:
            category_id (int): the id of the category to be returned

        dict: the catgory with the specified category id; None if no such
            category exists
        """
        try:
            db = get_db()
            query = "SELECT * FROM CATEGORIES WHERE CategoryID = ?"
            data = [category_id]
            result = db.execute(query, data)
            category = result.fetchone()
            if category is not None:
                category = dict(category)
            return category
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)


    @staticmethod
    def get_by_name(category_name):
        """Gets the row with the given category name from the categories table.
            
            If the database operations raise a sqlite3.Error, the method is 
            aborted with the status code 500.

        Args:
            category_name (str): the name of the category to be returned

        Returns:
            dict: the catgory with the specified name; None if no such 
                    catgory exists
        """
        try:
            db = get_db()
            query = "SELECT * FROM CATEGORIES WHERE CategoryName = ?"
            data = [category_name]
            result = db.execute(query, data)
            category = result.fetchone()
            if category is not None:
                category = dict(category)
            return category
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)


    @staticmethod
    def insert(category_data):
        """Inserts the specified category into the categories table.

            If the database operations raise a sqlite3.Error, the method is 
            aborted with the status code 500.

        Args:
            category_data (dict): the data of the category to be inserted;  
                must map "category_name" to a nonempty string.

        Returns:
            tuple: (success, message, category) where
                success (bool): True if the category has been inserted
                message (str): "The category has been inserted." if success is 
                    True; an error message if success is False
                category (dict): the inserted category; None if success is False
        """
        try:
            category_name = category_data["category_name"]
            success, message = CategoriesTable.validate_name(category_name)
            if not success:
                return False, message, None
            #if "category_name" not in category_data:
            #    return False, "Category name is missing.", None

            db = get_db()
            query = """
                INSERT INTO CATEGORIES (CategoryName) 
                VALUES (?)
            """
            data = [category_name]
            db.execute(query, data)
            category = CategoriesTable.get_by_name(category_name)
            db.commit()
            return True, "The category has been inserted.", category

        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)


    @staticmethod
    def delete(category_id):
        """Deletes the row with the specified id from the categories table.

            If the database operations raise a sqlite3.Error, the method is 
            aborted with the status code 500.

        Args:
            category_id (int): the id of the category to be deleted

        Returns:
            dict: the deleted category; None if there exists no category with 
                the specified id
        """
        try:
            db = get_db()
            category = CategoriesTable.get_by_id(category_id)
            if category is None:
                return None
            
            # This import statement has been placed inside the code
            # to avoid a circular import
            from model.products_table import ProductsTable
            if ProductsTable.get_by_category_id(category_id):
                return False, "The category cannot be deleted since it contains products.", None

            query = "DELETE FROM CATEGORIES WHERE CategoryID = ?"
            data = [category_id]
            db.execute(query, data)
            db.commit()
            return True, "The category has been deleted.", category

        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)


    @staticmethod
    def validate_name(name):
        """Checks if the specified name is a valid category name.

            If the necessary database operations raise a sqlite3.Error, 
            the method is aborted with the status code 500.

        Args:
            name (str): the category name to be validated
        
        Returns:
            tuple: (valid, message) where
                valid (bool): True if the category is valid
                message (str): "Category name is valid." if valid is 
                    True; an error message if valid is False
        """ 
        if name is None:
            return False, "Missing category name."

        if len(name) == 0:
            return False, "Category name cannot be empty."

        category = CategoriesTable.get_by_name(name)
        if category is not None:
            return False, "Category name exists already."

        return True, "Category name is valid."