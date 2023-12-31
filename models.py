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
@click.option("--role", prompt="Enter your role (stockmanager/user): ")
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