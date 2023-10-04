#Import necessary modules and libraries
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, Table, Column, Integer, String, Date
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import delete
import datetime
import click

# Create an engine for connecting to the SQLite database
engine = create_engine("sqlite:///many.db")

# Create a base class for declarative SQLAlchemy models
Base = declarative_base()

# Define the join table "orders"
orders = Table(
    "orders",
    Base.metadata,
    Column("order_id", Integer, primary_key=True),
    Column("customer_id", ForeignKey("customers.id")),
    Column("product_id", ForeignKey("products.id")),
    Column("order_date", Date),
    Column("quantity", Integer),
)

# Define the Product model
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer(), primary_key=True)
    name = Column(String())
    brand = Column(String())
    price = Column(Integer())
    quantity = Column(Integer())
    customers = relationship("Customer", secondary=orders, back_populates="products")


# Define the Customer model
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer(), primary_key=True)
    name = Column(String())
    email = Column(String())
    username = Column(String())
    role = Column(String())
    products = relationship("Product", secondary=orders, back_populates="customers")


# Function to get the most sold products from the database
def get_most_sold_products(session):
    # Query the database to get the products sorted by the total quantity sold in descending order
    # Return the sorted list of products
    products = (
        session.query(Product)
        .join(orders)
        .group_by(Product.id)
        .order_by(Product.quantity.desc())
        .all()
    )
    return products

# Function to get the least sold products from the database
def get_least_sold_products(session):
    # Query the database to get the products sorted by the total quantity sold in ascending order
    # Return the sorted list of products
    products = (
        session.query(Product)
        .join(orders)
        .group_by(Product.id)
        .order_by(Product.quantity)
        .all()
    )
    return products

# Function to get the products that have never been sold
def get_never_sold_products(session):
    # Query the database to get the products that have never been sold
    # Return the list of products
    products = (
        session.query(Product)
        .outerjoin(orders)
        .group_by(Product.id)
        .having(~orders.c.product_id.isnot(None))
        .all()
    )
    return products


# Function to get the products purchased within a specified date range
def get_products_purchased_in_date_range(session, start_date, end_date):
    # Query the database to get the products purchased within the specified date range
    # Return the list of products
    products = (
        session.query(Product)
        .join(orders)
        .filter(orders.c.order_date.between(start_date, end_date))
        .all()
    )
    return products

# Command-line interface function
@click.command()
@click.option("--role", prompt="Enter your role (store manager/user): ")
def main(role):
# Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()


    if role == "stockmanager":
                # Stock manager menu
        print("Menu:")
        print("1. Add a product")
        print("2. View available products")
        print("3. Update a product")
        print("4. Delete a product")
        print("5. Generate reports")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            # Add a product
            name = input("Enter product name: ")
            brand = input("Enter product brand: ")
            price = int(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))

            product = Product(name=name, brand=brand, price=price, quantity=quantity)
            session.add(product)
            session.commit()
            print("Product added successfully!")

        elif choice == "2":
            # View available products
            products = session.query(Product).all()
            print("Available products:")
            for product in products:
                print(
                    f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                )

        elif choice == "3":
            #updating a product
            product_id = int(input("Enter the ID of the product to update: "))
            product = session.query(Product).get(product_id)
            if product is None:
                print("Invalid product ID!")
            else:
                print("Menu:")
                print("1. Add quantity")
                print("2. Remove product")

                update_choice = input("Enter your choice: ")

                if update_choice == "1":
                    quantity = int(input("Enter the quantity to add: "))
                    product.quantity += quantity
                    session.commit()
                    print("Quantity added successfully!")
                elif update_choice == "2":
                    session.delete(product)
                    session.commit()
                    print("Product removed successfully!")
                else:
                    print("Invalid choice!")

        elif choice == "4":
            #deleting a product
            product_id = int(input("Enter the ID of the product to delete: "))
            delete_product = delete(Product).where(Product.id == product_id)
            session.execute(delete_product)
            session.commit()
            print("Product deleted successfully!")

        elif choice == "5":
            #Generate reports
            print("Report Menu:")
            print("1. Most sold products")
            print("2. Least sold products")
            print("3. Never sold products")
            print("4. Products purchased in a date range")

            report_choice = input("Enter choice: ")

            if report_choice == "1":
            # Most sold products report
                most_sold_products = get_most_sold_products(session)
                print("Most sold products:")
                for product in most_sold_products:
                    print(
                        f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                    )

            elif report_choice == "2":
            # Least sold products report
                least_sold_products = get_least_sold_products(session)
                print("Least sold products:")
                for product in least_sold_products:
                    print(
                        f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                    )

            elif report_choice == "3":
                # Never sold products report
                never_sold_products = get_never_sold_products(session)
                print("Never sold products:")
                for product in never_sold_products:
                    print(
                        f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                    )

            elif report_choice == "4":
            # Products purchased in a date range report
                start_date = input("Enter the start date (YYYY-MM-DD): ")
                end_date = input("Enter the end date (YYYY-MM-DD): ")
                products_purchased = get_products_purchased_in_date_range(
                    session, start_date, end_date
                )
                print("Products purchased in the specified date range:")
                for product in products_purchased:
                    print(
                        f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                    )

            else:
                print("Invalid choice!")

        elif choice == "6":
            # Exit the program
            return

        else:
            print("Invalid choice!")

    elif role == "user":
        # Code for user role
        username = input("Enter username: ")
        customer = session.query(Customer).filter_by(username=username).first()

        if customer is None:
            print("Invalid username!")
            return

        print("User menu:")
        print("1. View purchased products")
        print("2. Purchase a product")
        print("3. Exit")

        user_choice = input("Enter choice: ")

        if user_choice == "1":
            # View purchased products
            print("Products purchased:")
            for product in customer.products:
                print(
                    f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                )

        elif user_choice == "2":
            # Purchase a product
            product_id = int(input("Enter the ID of the product to purchase: "))
            product = session.query(Product).get(product_id)

            if product is None:
                print("Invalid product ID!")
            elif product.quantity <= 0:
                print("Product is out of stock!")
            else:
                quantity = int(input("Enter the quantity to purchase: "))
                if quantity <= product.quantity:
                    order_date = datetime.date.today()
                    order = orders.insert().values(
                        customer_id=customer.id,
                        product_id=product.id,
                        order_date=order_date,
                        quantity=quantity,
                    )
                    session.execute(order)
                    product.quantity -= quantity
                    session.commit()
                    print("Product purchased successfully!")
                else:
                    print("Insufficient quantity!")

        elif user_choice == "3":
            # Exit the program
            return

        else:
            print("Invalid choice!")

    else:
        print("Invalid role!")

    session.close()
    print("Exiting the menu.")


if __name__ == "__main__":
    # Create the database tables based on the defined models
    Base.metadata.create_all(engine)

    # main(None)
# Create a session and start the main CLI program
    Session = sessionmaker(bind=engine)
    session = Session()

    main()
    print("Exiting menu.")


# from sqlalchemy import create_engine
# from sqlalchemy import ForeignKey, Table, Column, Integer, String, CHAR, Date
# from sqlalchemy.orm import relationship, backref, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import delete
# from sqlalchemy import select

# engine = create_engine("sqlite:///many.db")
# Base = declarative_base()

# # Define the join table "orders"
# orders = Table(
#     "orders",
#     Base.metadata,
#     Column("order_id", Integer, primary_key=True),
#     Column("customer_id", ForeignKey("customers.id")),
#     Column("product_id", ForeignKey("products.id")),
#     Column("order_date", Integer),
#     Column("quantity", Integer),
# )


# class Product(Base):
#     __tablename__ = "products"
#     id = Column(Integer(), primary_key=True)
#     name = Column(String())
#     brand = Column(String())
#     price = Column(Integer())
#     quantity = Column(Integer())


# class Customer(Base):
#     __tablename__ = "customers"
#     id = Column(Integer(), primary_key=True)
#     name = Column(String())
#     email = Column(String())
#     username = Column(String())
#     role = Column(String())
#     orders = relationship("Product", secondary=orders, backref="customers")


# if __name__ == "__main__":
#     Base.metadata.create_all(engine)

#     Session = sessionmaker(bind=engine)
#     session = Session()

#     # Create products
#     product1 = Product(name="Television", brand="Samsung", price=60000, quantity=400)
#     product2 = Product(name="Radio", brand="JBL", price=46000, quantity=700)
#     product3 = Product(name="Smartphone", brand="iPhone", price=126000, quantity=900)
#     product4 = Product( name="Furniture", brand="Victoria Courts", price=148000, quantity=500
#     )
#     product5 = Product(name="Cutlery", brand="Vileroy", price=15000, quantity=200)
#     product6 = Product(name="Crockery", brand="Corelle", price=22000, quantity=270)
#     product7 = Product(name="Stationery", brand="Nataraj", price=13000, quantity=470)
#     product8 = Product(name="Clothing", brand="Gucci", price=155000, quantity=100)
#     product9 = Product(name="Shoes", brand="Nike", price=190000, quantity=1000)
#     product10 = Product(
#         name="Digital camera", brand="Kodack", price=140000, quantity=150
#     )
#     product11 = Product(name="Gaming console", brand="Xbox", price=80000, quantity=70)

#     session.add_all(
#         [
#             product1,
#             product2,
#             product3,
#             product4,
#             product5,
#             product6,
#             product7,
#             product8,
#             product9,
#             product10,
#             product11,
#         ]
#     )
#     # session.commit()

#     # Create customers
#     customer1 = Customer(
#         name="Morgan Jason",
#         email="420morganjason@gmail.com",
#         username="morganjason420",
#         role="store manager",
#     )
#     customer2 = Customer(
#         name="Mike Tyson",
#         email="421miketyson@gmail.com",
#         username="miketyson421",
#         role="customer",
#     )
#     customer3 = Customer(
#         name="Muhammed Ali",
#         email="422muhammedali@gmail.com",
#         username="muhammedali422",
#         role="customer",
#     )
#     customer4 = Customer(
#         name="Vybz Kartel",
#         email="423vybzkartel@gmail.com",
#         username="vybzkartel423",
#         role="store manager",
#     )
#     customer5 = Customer(
#         name="Lebron James",
#         email="424lebronjames@gmail.com",
#         username="lebronjames424",
#         role="store manager",
#     )
#     customer6 = Customer(
#         name="Ashanti Veron",
#         email="425ashantiveron@gmail.com",
#         username="ashantiveron425",
#         role="customer",
#     )
#     customer7 = Customer(
#         name="Aaliyah Biggie",
#         email="426aaliyahbiggie@gmail.com",
#         username="Aaliyahbiggie426",
#         role="customer",
#     )
#     customer8 = Customer(
#         name="Santan Dave",
#         email="427santandave@gmail.com",
#         username="Santandave427",
#         role="customer",
#     )
#     customer9 = Customer(
#         name="Robert Nesta",
#         email="428robertnesta@gmail.com",
#         username="robertnesta428",
#         role="store manager",
#     )
#     customer10 = Customer(
#         name="Popcaan Unruly",
#         email="429popcaanunruly@gmail.com",
#         username="popcaanunruly429",
#         role="store manager",
#     )
#     customer11 = Customer(
#         name="Skillibeng Eside",
#         email="430skillibengeside@gmail.com",
#         username="skillibengeside430",
#         role="customer",
#     )

#     session.add_all(
#         [
#             customer1,
#             customer2,
#             customer3,
#             customer4,
#             customer5,
#             customer6,
#             customer7,
#             customer8,
#             customer9,
#             customer10,
#             customer11,
#         ]
#     )
#     # session.commit()
#     #


# # Delete a specific row from the orders table
# # delete_order = delete(orders).where(orders.c.order_id == 5)
# # session.execute(delete_order)
# # session.commit()

# # # Add items to the orders
# # order1 = orders.insert().values(
# #     customer_id=1, product_id=1, order_date="2023-06-06", quantity=3
# # )
# # order2 = orders.insert().values(
# #     customer_id=2, product_id=4, order_date="2023-06-06", quantity=2
# # )
# # order3 = orders.insert().values(
# #     customer_id=1, product_id=3, order_date="2023-06-07", quantity=1
# # )
# # order4 = orders.insert().values(
# #     customer_id=4, product_id=4, order_date="2023-06-08", quantity=5
# # )
# # order5 = orders.insert().values(
# #     customer_id=3, product_id=2, order_date="2023-06-08", quantity=4
# # )
# # order6 = orders.insert().values(
# #     customer_id=1, product_id=1, order_date="2023-06-09", quantity=2
# # )
# # order7 = orders.insert().values(
# #     customer_id=3, product_id=1, order_date="2023-06-09", quantity=1
# # )

# # session.execute(order1)
# # session.execute(order2)
# # session.execute(order3)
# # session.execute(order4)
# # session.execute(order5)
# # session.execute(order6)
# # session.execute(order7)
# # session.commit()
# from sqlalchemy import create_engine
# from sqlalchemy import ForeignKey, Table, Column, Integer, String, Date
# from sqlalchemy.orm import relationship, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import delete
# import datetime
# import click

# engine = create_engine("sqlite:///many.db")
# Base = declarative_base()

# # Define the join table "orders"
# orders = Table(
#     "orders",
#     Base.metadata,
#     Column("order_id", Integer, primary_key=True),
#     Column("customer_id", ForeignKey("customers.id")),
#     Column("product_id", ForeignKey("products.id")),
#     Column("order_date", Date),
#     Column("quantity", Integer),
# )


# class Product(Base):
#     __tablename__ = "products"
#     id = Column(Integer(), primary_key=True)
#     name = Column(String())
#     brand = Column(String())
#     price = Column(Integer())
#     quantity = Column(Integer())


# class Customer(Base):
#     __tablename__ = "customers"
#     id = Column(Integer(), primary_key=True)
#     name = Column(String())
#     email = Column(String())
#     username = Column(String())
#     role = Column(String())
#     orders = relationship("Product", secondary=orders, backref="customers")


# @click.command()
# @click.option("--role", prompt="Enter your role (stockmanager/user): ")
# def main(role):
#     if role == "stockmanager":
#         print("Menu:")
#         print("1. Add a product")
#         print("2. View available products")
#         print("3. Update a product")
#         print("4. Delete a product")
#         print("5. Exit")

#         choice = input("Enter your choice: ")

#         if choice == "1":
#             name = input("Enter product name: ")
#             brand = input("Enter product brand: ")
#             price = int(input("Enter product price: "))
#             quantity = int(input("Enter product quantity: "))

#             product = Product(name=name, brand=brand, price=price, quantity=quantity)
#             session.add(product)
#             session.commit()
#             print("Product added successfully!")

#         elif choice == "2":
#             products = session.query(Product).all()
#             print("Available products:")
#             for product in products:
#                 print(
#                     f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
#                 )

#         elif choice == "3":
#             product_id = int(input("Enter the ID of the product to update: "))
#             product = session.query(Product).get(product_id)
#             if product is None:
#                 print("Invalid product ID!")
#             else:
#                 print("Menu:")
#                 print("1. Add quantity")
#                 print("2. Remove product")

#                 update_choice = input("Enter your choice: ")

#                 if update_choice == "1":
#                     quantity = int(input("Enter the quantity to add: "))
#                     product.quantity += quantity
#                     session.commit()
#                     print("Quantity added successfully!")
#                 elif update_choice == "2":
#                     session.delete(product)
#                     session.commit()
#                     print("Product removed successfully!")
#                 else:
#                     print("Invalid choice!")

#         elif choice == "4":
#             product_id = int(input("Enter the ID of the product to delete: "))
#             delete_product = delete(Product).where(Product.id == product_id)
#             session.execute(delete_product)
#             session.commit()
#             print("Product deleted successfully!")

#         elif choice == "5":
#             return

#         else:
#             print("Invalid choice!")

#     elif role == "user":
#         username = input("Enter your username: ")
#         customer = session.query(Customer).filter_by(username=username).first()

#         if customer is None:
#             print("Invalid username!")
#         else:
#             product_id = int(
#                 input("Enter the ID of the product you want to purchase: ")
#             )
#             quantity = int(input("Enter the quantity to purchase: "))

#             product = session.query(Product).get(product_id)
#             if product is None:
#                 print("Invalid product ID!")
#             elif quantity > product.quantity:
#                 print("Insufficient quantity!")
#             else:
#                 product.quantity -= quantity
#                 order = orders.insert().values(
#                     customer_id=customer.id,
#                     product_id=product_id,
#                     order_date=datetime.date.today(),
#                     quantity=quantity,
#                 )
#                 session.execute(order)
#                 session.commit()
#                 print("Order placed successfully!")

#     else:
#         print("Invalid role!")

#     print()


# if __name__ == "__main__":
#     Base.metadata.create_all(engine)

#     Session = sessionmaker(bind=engine)
#     session = Session()

#     main()
#     print("Exiting the menu.")
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, Table, Column, Integer, String, Date
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import delete
import datetime
import click

engine = create_engine("sqlite:///many.db")
Base = declarative_base()

# Define the join table "orders"
orders = Table(
    "orders",
    Base.metadata,
    Column("order_id", Integer, primary_key=True),
    Column("customer_id", ForeignKey("customers.id")),
    Column("product_id", ForeignKey("products.id")),
    Column("order_date", Date),
    Column("quantity", Integer),
)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer(), primary_key=True)
    name = Column(String())
    brand = Column(String())
    price = Column(Integer())
    quantity = Column(Integer())
    customers = relationship("Customer", secondary=orders, back_populates="products")


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer(), primary_key=True)
    name = Column(String())
    email = Column(String())
    username = Column(String())
    role = Column(String())
    products = relationship("Product", secondary=orders, back_populates="customers")


def get_most_sold_products(session):
    # Query the database to get the products sorted by the total quantity sold in descending order
    # Return the sorted list of products
    products = (
        session.query(Product)
        .join(orders)
        .group_by(Product.id)
        .order_by(Product.quantity.desc())
        .all()
    )
    return products


def get_least_sold_products(session):
    # Query the database to get the products sorted by the total quantity sold in ascending order
    # Return the sorted list of products
    products = (
        session.query(Product)
        .join(orders)
        .group_by(Product.id)
        .order_by(Product.quantity)
        .all()
    )
    return products


def get_never_sold_products(session):
    # Query the database to get the products that have never been sold
    # Return the list of products
    products = (
        session.query(Product)
        .outerjoin(orders)
        .group_by(Product.id)
        .having(~orders.c.product_id.isnot(None))
        .all()
    )
    return products


def get_products_purchased_in_date_range(session, start_date, end_date):
    # Query the database to get the products purchased within the specified date range
    # Return the list of products
    products = (
        session.query(Product)
        .join(orders)
        .filter(orders.c.order_date.between(start_date, end_date))
        .all()
    )
    return products


@click.command()
@click.option("--role", prompt="Enter your role (store manager/user): ")
def main(role):
    if role == "stockmanager":
        print("Menu:")
        print("1. Add a product")
        print("2. View available products")
        print("3. Update a product")
        print("4. Delete a product")
        print("5. Generate reports")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter product name: ")
            brand = input("Enter product brand: ")
            price = int(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))

            product = Product(name=name, brand=brand, price=price, quantity=quantity)
            session.add(product)
            session.commit()
            print("Product added successfully!")

        elif choice == "2":
            products = session.query(Product).all()
            print("Available products:")
            for product in products:
                print(
                    f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                )

        elif choice == "3":
            # Code for updating a product
            product_id = int(input("Enter the ID of the product to update: "))
            product = session.query(Product).get(product_id)
            if product is None:
                print("Invalid product ID!")
            else:
                print("Menu:")
                print("1. Add quantity")
                print("2. Remove product")

                update_choice = input("Enter your choice: ")

                if update_choice == "1":
                    quantity = int(input("Enter the quantity to add: "))
                    product.quantity += quantity
                    session.commit()
                    print("Quantity added successfully!")
                elif update_choice == "2":
                    session.delete(product)
                    session.commit()
                    print("Product removed successfully!")
                else:
                    print("Invalid choice!")

        elif choice == "4":
            # Code for deleting a product
            product_id = int(input("Enter the ID of the product to delete: "))
            delete_product = delete(Product).where(Product.id == product_id)
            session.execute(delete_product)
            session.commit()
            print("Product deleted successfully!")

        elif choice == "5":
            print("Report Menu:")
            print("1. Most sold products")
            print("2. Least sold products")
            print("3. Never sold products")
            print("4. Products purchased in a date range")

            report_choice = input("Enter your choice: ")

            if report_choice == "1":
                most_sold_products = get_most_sold_products(session)
                print("Most sold products:")
                for product in most_sold_products:
                    print(
                        f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                    )

            elif report_choice == "2":
                least_sold_products = get_least_sold_products(session)
                print("Least sold products:")
                for product in least_sold_products:
                    print(
                        f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                    )

            elif report_choice == "3":
                never_sold_products = get_never_sold_products(session)
                print("Never sold products:")
                for product in never_sold_products:
                    print(
                        f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                    )

            elif report_choice == "4":
                start_date = input("Enter the start date (YYYY-MM-DD): ")
                end_date = input("Enter the end date (YYYY-MM-DD): ")
                products_purchased = get_products_purchased_in_date_range(
                    session, start_date, end_date
                )
                print("Products purchased in the specified date range:")
                for product in products_purchased:
                    print(
                        f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, Price: {product.price}, Quantity: {product.quantity}"
                    )

            else:
                print("Invalid choice!")

        elif choice == "6":
            return

        else:
            print("Invalid choice!")

    elif role == "user":
        # Code for user role
        username = input("Enter your username: ")
        customer = session.query(Customer).filter_by(username=username).first()

        if customer is None:
            print("Invalid username!")

    else:
        print("Invalid role!")

    print()


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    main()
    print("Exiting the menu.")