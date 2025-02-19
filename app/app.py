from flask import Flask, render_template
from model.database import close_db
from model.products_table import ProductsTable


app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(error):
    """Returns a 404-error message page

    Args:
        error (werkzeug.exception.NotFound): error object

    Returns:
        Response: 404-error message page
    """
    return render_template("errors/404.jinja"), 404


@app.route("/")
@app.route("/index")
def home():
    """Returns the homepage

    Returns:
        Response: the homepage
    """
    return render_template("index.jinja")


@app.route("/product")
def product_list():
    """Returns a page listing all products

    Returns:
        Response: the product page
    """
    products = ProductsTable.get()
    return render_template("product_list.jinja", products=products)


@app.route("/order")
def orders():
    """Returns a page listing all orders

    Returns:
        Response: the orders page
    """
    # orders = OrdersTable.get()
    return render_template("orders.jinja")


@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection

    Args:
        exception (sqlite3.Error): The error raised if the close operation fails;
            Otherwise, None.
    """
    close_db()


@app.errorhandler(500)
def internal_server_error(error):
    """Returns a 500 error message
    Args:
        error: 500 Internal Server Error

    Returns:
        Response: 500-error message page
    """
    return render_template("errors/500.jinja"), 500
