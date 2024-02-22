import pandas as pd

from app import db
from app import login_manager, app
from datetime import datetime
from flask_wtf import FlaskForm
from flask_user import UserMixin
from flask_user import UserManager
from wtforms import EmailField
from wtforms import SubmitField
from wtforms import StringField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import DataRequired
from flask_wtf.file import FileField
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

# Create Users Models

    # Create the RegisterForm class with db.Model
class RegisterForms(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User Autentication
    email = db.Column(db.Unicode(255), unique=True,
                      nullable=False, server_default=u'')
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # User Information
    active = db.Column('is_active', db.Boolean(),
                        nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    work_id = db.Column(db.Integer(), db.ForeignKey("locations.id"))
    role_id = db.Column(db.Integer(),  db.ForeignKey("roles.id"))
    
    def __repr__(self) -> str:
        return f'<User {self.first_name} {self.last_name}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def save(self:"RegisterForms"):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(_id:int) -> str:
        return RegisterForms.query.get(_id).first()
    
    @staticmethod
    def get_by_email(email:str):
        return RegisterForms.query.filter_by(email=email).first()

    # Create the Role class with db.Model

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False,
                    server_default='', unique=True)
    label = db.Column(db.Unicode(255), nullable=False, server_default='')
    users = db.relationship("RegisterForms", backref=db.backref("roles"))

    # Create the Location class with db.Model

class Location(db.Model):
    __tablename__ = "locations"
    
    id    = db.Column(db.Integer(), primary_key=True)
    place = db.Column(db.String(50), nullable=False,
                    server_default='',unique=True)
    users = db.relationship("RegisterForms", 
                            backref=db.backref("location"))
    locations = db.relationship("Employee", 
                            backref=db.backref("location"))
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    # Create the Employee class with db.Model

class Employee(db.Model):
    """
    assistance_id = 0 => Non Defined
    """
    __tablename__ = "employee"
    
    id = db.Column(db.Integer(), primary_key=True)
    
    employee_id = db.Column(db.Integer())
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Relationship Fields
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    

class Assistance(db.Model):
    """
    Table to store the no completed assistance
    """
    
    __tablename__ = "assistance"
    
    id = db.Column(db.Integer(), primary_key=True)
    
    employee_id = db.Column(db.Integer(), nullable=False)
    arrive_time = db.Column(db.DateTime(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    month = db.Column(db.String())
    date = db.Column(db.String())
    arrive_hour = db.Column(db.String(), nullable=False)
    
    @classmethod
    def save_assistance(cls, df:pd.DataFrame):
        # Erase all the data in the table
        Assistance.query.delete()
        # Reset Index
        query = f"ALTER SEQUENCE {cls.__tablename__}_id_seq RESTART WITH 1;"
        db.session.execute(query)
        db.session.commit()
        
        # As it's a df
        df.to_sql(name="assistance", con=db.engine, if_exists="append", index=False)


# Create Forms

    # Create the LoginForm class with FlaskForm
class LoginForm(FlaskForm):
    email = EmailField('Email Addres', validators=[
                        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Sign In')
    remember = BooleanField('Remember Me')

    # Create the PageRegisterForm class with FlaskForm

class PageRegisterForm(FlaskForm):
    first_name = StringField('First Name',
                              validators=[DataRequired(),
                                        Length(1, 50)])
    last_name = StringField('Last Name',
                            validators=[DataRequired(),
                                        Length(1, 50)])
    email = EmailField('Email Address',
                        validators=[DataRequired(),
                                    Length(1, 64)])
    password = PasswordField("Password",
                            validators=[DataRequired(),
                                        EqualTo("password_confirmer", message="Las contraseñas deben coincidir")])
    password_confirmer = PasswordField('Repeat Password')
    agree_to_terms = BooleanField('Agree to Terms', validators=[DataRequired()])
    work_id = SelectField("Tienda", choices=[(2, "Oficina Principal"),
                                            (3, "Tienda Nicollini"),
                                            (4, "Tienda Ferretero")])
    register = SubmitField()

    # Create form for upload a file

class FileLoader(FlaskForm):
    file_oficina_principal = FileField(label="Oficina Principal")
    file_nicollini = FileField(label="Tienda Nicollini")
    file_ferretero = FileField(label="Tienda Ferretero")
    submit = SubmitField()


class FilterForm(FlaskForm):
    # Get employees id from the database to use in the form selection
    with app.app_context():
        employees = Employee.get_all()
        choices_employee = [(0, "Todos")]
        choices_employee_to_add = [(employee.employee_id, f"{employee.first_name} {employee.last_name}") for employee in employees]
        choices_employee.extend(choices_employee_to_add)
    

    # Get locations id from the database to use in the form selection
    with app.app_context():
        locations = Location.get_all()
        choices_location = [(0, "Todos")]
        choices_employee_to_add = [(location.id, location.place) for location in locations]
        choices_location.extend(choices_employee_to_add)

    print(choices_employee)

    employee_name = SelectField("Empleado", choices=choices_employee, default=9)
    location = SelectField("Tienda", choices=choices_location, default=0)
    month = SelectField("Mes", choices=[(1, "January"), (2, "February"), (3, "March"), 
                                        (4, "April"), (5, "May"), (6, "June"), 
                                        (7, "July"), (8, "August"), (9, "September"), 
                                        (10, "October"), (11, "November"), (12, "Dicember")], 
                                default=datetime.now().month)
    submit = SubmitField()


# Configurations

@login_manager.user_loader
def load_user(id):
    return RegisterForms.query.get(int(id))

user_manager = UserManager(app, db, RegisterForms)