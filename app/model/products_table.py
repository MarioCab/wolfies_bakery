from flask import abort
import sqlite3
import re
from model.database import get_db
from model.categories_table import CategoriesTable


class ProductsTable:
    @staticmethod
    def get():
        """Gets all rows from the products .

            If the database operations raise a sqlite3.Error, the method is
            aborted with the status code 500.

        Returns:
            list: a list of all rows; each row is a dictionary that maps column
                names to values. An empty list if the table has no rows.
        """
        try:
            db = get_db()
            result = db.execute("SELECT * FROM PRODUCTS")
            products = result.fetchall()
            products = [dict(product) for product in products]
            return products
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def get_by_category_id(category_id):
        """Gets the rows with the given category id from the products table.

            If the database operations raise a sqlite3.Error, the method is
            aborted with the status code 500.

        Args:
            category_id (int): the category id of the products to be returned

        Returns:
            list: a list of all rows with the specified category id; each row
                is a dictionary that maps column names to values. An empty list
                if there are not products with the specified category id.
        """
        try:
            db = get_db()
            query = "SELECT * FROM PRODUCTS WHERE CategoryID = ?"
            data = [category_id]
            result = db.execute(query, data)
            products = result.fetchall()
            products = [dict(product) for product in products]
            return products
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def get_by_id(product_id):
        """Gets the row with the specified id from the products table.

            If the database operations raise a sqlite3.Error, the method is
            aborted with the status code 500.

        Args:
            product_id (int): the id of the product to be returned

        Returns:
            dict: the product with the specified product id; None if no such
                product exists
        """
        try:
            db = get_db()
            query = "SELECT * FROM PRODUCTS WHERE ProductID = ?"
            data = [product_id]
            result = db.execute(query, data)
            product = result.fetchone()
            if product is not None:
                product = dict(product)
            return product
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def get_by_code(product_code):
        """Gets the row with the given product code from the products table.

            If the database operations raise a sqlite3.Error, the method is
            aborted with the status code 500.

        Args:
            product_code (str): the code of the product to be returned

        Returns:
            dict: the product with the specified product code, None if no
                such product exists
        """
        try:
            db = get_db()
            query = "SELECT * FROM PRODUCTS WHERE ProductCode = ?"
            data = [product_code]
            result = db.execute(query, data)
            product = result.fetchone()
            if product is not None:
                product = dict(product)
            return product
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def insert(product_data):
        """Inserts the specified product into the products table.

            If the database operations raise a sqlite3.Error, the method is
            aborted with the status code 500.

        Args:
            product_data (dict): the data of the product to be inserted;
                must map
                    "category_id" to an existing category id
                    "product_code" to a nonempty, not yet existing code
                    "product_name" to a nonempty name
                    "price" to a nonnegative number

        Returns:
            tuple: (success, message, category) where
                success (bool): True if the product has been inserted
                message (str): "The product has been inserted." if success is
                    True; an error message if success is False
                category (dict): the inserted product; None if success is False
        """
        try:
            valid, message = ProductsTable.validate_data_for_insert(product_data)
            if not valid:
                return False, message, None

            db = get_db()
            query = """
                INSERT INTO PRODUCTS (CategoryID, ProductCode, ProductName, Price) 
                VALUES (?, ?, ?, ?)
            """
            data = [
                product_data["category_id"],
                product_data["product_code"],
                product_data["product_name"],
                product_data["price"],
            ]
            db.execute(query, data)
            product = ProductsTable.get_by_code(product_data["product_code"])
            db.commit()
            return True, "The product has been inserted", product

        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def update(product_id, product_data):
        """Updates the product data of the row with the specified product id.

            If the database operations raise a sqlite3.Error, the method is
            aborted with the status code 500.

        Args:
            product_id (int): the id of the product to be updated
            product (dict): the new product data; must map
                "category_id" to an existing category id
                "product_code" to a nonempty, unique code
                "product_name" to a nonempty name
                "price" to a nonnegative number

        Returns:
            tuple: (success, message, category) where
                success (bool): True if the product has been updated
                message (str): "The product has been inserted." if success is
                    True; an error message if success is False
                category (dict): the updated product; None if success is False
        """
        try:
            valid, message = ProductsTable.validate_data_for_update(
                product_id, product_data
            )
            if not valid:
                return False, message, None

            db = get_db()
            query = """
                UPDATE PRODUCTS 
                SET CategoryID = ?,
                    ProductCode = ?,
                    ProductName = ?,
                    Price = ? 
                WHERE ProductID = ?
            """
            data = [
                product_data["category_id"],
                product_data["product_code"],
                product_data["product_name"],
                product_data["price"],
                product_id,
            ]
            db.execute(query, data)
            product = ProductsTable.get_by_code(product_data["product_code"])
            db.commit()
            return True, "The product has been updated.", product

        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def delete(product_id):
        """Deletes the row with the given product id from the products table.

            If the database operations raise a sqlite3.Error, the method is
            aborted with the status code 500.

        Args:
            product_id (int): the id of the product to be deleted

        Returns:
            dict: the deleted product; None if there exists no product with
                the specified id.
        """
        try:
            db = get_db()
            product = ProductsTable.get_by_id(product_id)
            if product is None:
                return None
            query = "DELETE FROM PRODUCTS WHERE ProductID = ?"
            data = [product_id]
            db.execute(query, data)
            db.commit()
            return product
        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def validate_data_for_update(product_id, product_data):
        """Checks if the specified product data is valid.

            The specified data is the new data of the existing product with
            with the specified product id.
            If the necessary database operations raise a sqlite3.Error,
            the method is aborted with the status code 500.

        Args:
            product_id (int): the id of the product to be updated
            product (dict): the new product data

        Returns:
            tuple: (valid, message) where
                valid (bool): True if the product data is valid
                message (str): "The product data is valid." if valid is
                    True; an error message if valid is False
        """
        try:
            if ProductsTable.get_by_id(product_id) is None:
                return False, "There is no product with the specified id."

            valid, message = ProductsTable.validate_updated_code(
                product_data["product_code"]
                if "product_code" in product_data
                else None,
                product_id,
            )
            if not valid:
                return False, message

            valid, message = ProductsTable.validate_name(
                product_data["product_name"] if "product_name" in product_data else None
            )
            if not valid:
                return False, message

            valid, message = ProductsTable.validate_category_id(
                product_data["category_id"] if "category_id" in product_data else None
            )
            if not valid:
                return False, message

            valid, message = ProductsTable.validate_price(
                product_data["price"] if "price" in product_data else None
            )
            if not valid:
                return False, message

            return True, "The product data is valid."

        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def validate_data_for_insert(product_data):
        """Checks if the specified product data is valid.

            The specified data is the data of a new product.
            If the necessary database operations raise a sqlite3.Error,
            the method is aborted with the status code 500.

        Args:
            product (dict): the new product data to be validated

        Returns:
            tuple: (valid, message) where
                valid (bool): True if the product data is valid
                message (str): "The product data is valid." if valid is
                    True; an error message if valid is False
        """
        try:
            valid, message = ProductsTable.validate_code(
                product_data["product_code"] if "product_code" in product_data else None
            )
            if not valid:
                return False, message

            valid, message = ProductsTable.validate_name(
                product_data["product_name"] if "product_name" in product_data else None
            )
            if not valid:
                return False, message

            valid, message = ProductsTable.validate_category_id(
                product_data["category_id"] if "category_id" in product_data else None
            )
            if not valid:
                return False, message

            valid, message = ProductsTable.validate_price(
                product_data["price"] if "price" in product_data else None
            )
            if not valid:
                return False, message

            return True, "The product data is valid."

        except sqlite3.Error as error:
            print("ERROR: " + str(error))
            abort(500)

    @staticmethod
    def validate_code(code):
        """Checks if the specified code is a valid product code.

            If the necessary database operations raise a sqlite3.Error,
            the method is aborted with the status code 500.

        Args:
            code (str): the product code of a new product to be validated

        Returns:
            tuple: (valid, message) where
                valid (bool): True if the product code is valid
                message (str): "Product code is valid." if valid is
                    True; an error message if valid is False
        """
        if code is None:
            return False, "Missing product code."

        if len(code) == 0:
            return False, "Product code cannot be empty."

        if ProductsTable.get_by_code(code) is not None:
            return False, "Product code exists already."

        return True, "Product code is valid."

    @staticmethod
    def validate_updated_code(code, product_id):
        """Checks if the given code is valid for the product with the given id.

            If the necessary database operations raise a sqlite3.Error,
            the method is aborted with the status code 500.

        Args:
            code (str): the product code of an existing product to be validated
            product_id (int): the id of the product to be updated

        Returns:
            tuple: (valid, message) where
                valid (bool): True if the product code is valid
                message (str): "Product code is valid." if valid is
                    True; an error message if valid is False
        """
        if code is None:
            return False, "Missing product code."

        if len(code) == 0:
            return False, "Product code cannot be empty."

        tmp_product = ProductsTable.get_by_code(code)
        if tmp_product is not None and tmp_product["ProductID"] is not int(product_id):
            return False, "Product code exists already."

        return True, "Product code is valid."

    @staticmethod
    def validate_name(name):
        """Checks if the specified name is a valid product name.

            If the necessary database operations raise a sqlite3.Error,
            the method is aborted with the status code 500.

        Args:
            name (str): the product name to be validated

        Returns:
            tuple: (valid, message) where
                valid (bool): True if the product name is valid
                message (str): "Product name is valid." if valid is
                    True; an error message if valid is False
        """
        if name is None:
            return False, "Missing product name."

        if len(name) == 0:
            return False, "Product name cannot be empty."
        elif len(name) < 3:
            return False, "Product name must have at least characters."

        return True, "Product name is valid."

    @staticmethod
    def validate_category_id(category_id):
        """Checks if the specified id is the id of an existing category.

            If the necessary database operations raise a sqlite3.Error,
            the method is aborted with the status code 500.

        Args:
            category_id (int): the category id to be validated

        Returns:
            tuple: (valid, message) where
                valid (bool): True if the category id exists
                message (str): "Product name is valid." if valid is
                    True; an error message if valid is False
        """
        if category_id is None:
            return False, "Missing category id."

        category = CategoriesTable.get_by_id(category_id)
        if category is None:
            return False, "Category ID does not exist."

        return True, "Category id is valid."

    @staticmethod
    def validate_price(price):
        """Checks if the specified price represents a valid price.

            If the necessary database operations raise a sqlite3.Error,
            the method is aborted with the status code 500.

        Args:
            price (float): the price to be validated

        Returns:
            tuple: (valid, message, price) where
                valid (bool): True if the price is valid
                message (str): "Product name is valid." if valid is
                    True; an error message if valid is False
        """
        if price is None:
            return False, "Missing price."

        if price < 0:
            return False, "Price must be a nonnegative value."

        return True, "Price is valid."

    @staticmethod
    def validate_price_string(price):
        """Checks if the specified string represents a valid price.

            If the necessary database operations raise a sqlite3.Error,
            the method is aborted with the status code 500

        Args:
            price (str): the price to be validated

        Returns:
            tuple: (valid, message, price) where
                valid (bool): True if the price is valid
                message (str): "Product name is valid." if valid is
                    True; an error message if valid is False
        """
        if price is None:
            return False, "Missing price."

        if len(price) == 0:
            return False, "Price cannot be empty."

        if re.search("^\d*[.]\d\d$|^\d*$", price) is None:
            return False, "Price must be a nonnegative value with two decimal places."

        return True, "Price is valid."
