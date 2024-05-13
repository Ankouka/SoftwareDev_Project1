from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField,  SubmitField, validators, IntegerField, BooleanField, FloatField, FieldList
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class SignUpForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    about = TextAreaField('About')
    passwd = PasswordField('Password', validators=[DataRequired()])
    passwd_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class SignInForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    passwd = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class ItemForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    sku = IntegerField('Product code')
    price = FloatField('Product Price', validators=[DataRequired()])
    #product_image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png'])])
    product_image = StringField('Product Image', validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired()])
    specs = StringField('Specs')
    submit = SubmitField('Confirm')

class ProductForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    available = BooleanField('Available', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class OrderForm(FlaskForm):
    id = IntegerField('Order ID')
    