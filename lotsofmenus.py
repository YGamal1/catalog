#!/usr/bin/env python2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Categorie, Base, CategorieItem, User

engine = create_engine('postgresql://catalog:catalog/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="yehia gamal", email="yehiagamal99@gmail.com",
             picture='https://lh5.googleusercontent.com/-kbCg3VG5U2I/AAAAAAAAAAI/AAAAAAAAADI/qCwI4RIs3kE/photo.jpg')
session.add(User1)
session.commit()

# Items for Soccer
categorie1 = Categorie(name="Soccer", id=1)

session.add(categorie1)
session.commit()

categorieitem1 = CategorieItem(user_id=1,
    name="Two Shinguards",
    description="best for any condetion",
    categorie=categorie1)

session.add(categorieitem1)
session.commit()


categorieitem2 = CategorieItem(user_id=1,
    name="Shinguards",
    description="the shinguards ",
    categorie=categorie1)

session.add(categorieitem2)
session.commit()

categorieitem3 = CategorieItem(user_id=1,
    name="Jersey",
    description="the shirt",
    categorie=categorie1)

session.add(categorieitem3)
session.commit()

categorieitem4 = CategorieItem(user_id=1,
    name="Soccer Cleats",
    description="The shoes",
    categorie=categorie1)

session.add(categorieitem4)
session.commit()


# Items for Basketball
categorie2 = Categorie(name="Basketball", id=2)

session.add(categorie2)
session.commit()


categorieitem1 = CategorieItem(user_id=1,
    name="Basketball Cleats",
    description="the basketball cleats",
    categorie=categorie2)

session.add(categorieitem1)
session.commit()


# Items for Baseball
categorie3 = Categorie(name="Baseball", id=3)

session.add(categorie3)
session.commit()


categorieitem1 = CategorieItem(user_id=1,
    name="Bat",
    description="the bat",
    categorie=categorie3)

session.add(categorieitem1)
session.commit()


# Items for Frisbee
categorie4 = Categorie(name="Frisbee", id=4)

session.add(categorie4)
session.commit()


categorieitem1 = CategorieItem(user_id=1,
    name="Frisbee",
    description="the frisbee",
    categorie=categorie4)

session.add(categorieitem1)
session.commit()


# Items for Snowboarding
categorie5 = Categorie(name="Snowboarding", id=5)

session.add(categorie5)
session.commit()


categorieitem1 = CategorieItem(user_id=1,
    name="Goggles",
    description="the goggles",
    categorie=categorie5)

session.add(categorieitem1)
session.commit()

categorieitem2 = CategorieItem(user_id=1,
    name="Snowboard",
    description="the snowboard",
    categorie=categorie5)

session.add(categorieitem2)
session.commit()


# Items for Rock Climping
categorie6 = Categorie(name="Rock Climping", id=6)

session.add(categorie6)
session.commit()


categorieitem1 = CategorieItem(user_id=1,
    name="Climping",
    description="the climping",
    categorie=categorie6)

session.add(categorieitem1)
session.commit()


# Items for Foosball
categorie7 = Categorie(name="Foosball", id=7)

session.add(categorie7)
session.commit()


categorieitem1 = CategorieItem(user_id=1,
    name="Foosball",
    description="the foosball",
    categorie=categorie7)

session.add(categorieitem1)
session.commit()


# Items for Skating
categorie8 = Categorie(name="Skating", id=8)

session.add(categorie8)
session.commit()


categorieitem1 = CategorieItem(user_id=1,
    name="Skating",
    description="the skating",
    categorie=categorie8)

session.add(categorieitem1)
session.commit()


# Items for Hockey
categorie9 = Categorie(name="Hockey", id=9)

session.add(categorie9)
session.commit()


categorieitem1 = CategorieItem(user_id=1,
    name="Stik",
    description="the stik",
    categorie=categorie9)

session.add(categorieitem1)
session.commit()

print("added items!")
