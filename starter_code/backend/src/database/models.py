import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

def setup_db(app):
    '''
    Binds a flask application and a SQLAlchemy service.
    '''
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

def db_drop_and_create_all():
    '''
    Drops the database tables and starts fresh.
    Can be used to initialize a clean database.
    '''
    db.drop_all()
    db.create_all()

    # add one demo row which is helping in POSTMAN test
    drink = Drink(
        title='water',
        recipe='[{"name": "water", "color": "blue", "parts": 1}]'
    )

    drink.insert()

class Drink(db.Model):
    '''
    A persistent drink entity, extends the base SQLAlchemy Model
    '''

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe = Column(String(180), nullable=False)

    def short(self):
        '''
        Short form representation of the Drink model
        '''

        print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    def long(self):
        '''
        Long form representation of the Drink model
        '''

        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    def insert(self):
        '''
        Inserts a new model into a database.
        '''

        db.session.add(self)
        db.session.commit()

    def delete(self):
        '''
        Deletes a new model into a database.
        '''

        db.session.delete(self)
        db.session.commit()

    def update(self):
        '''
        Updates a new model into a database.
        '''

        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())
