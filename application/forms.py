import concurrent.futures as cf

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (HiddenField, IntegerField, PasswordField, SelectField,
                     StringField, SubmitField)
from wtforms.fields.core import SelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from application import lookup
from application.models import Holdings, Users


class RegisterForm(FlaskForm):

    # the func name is specific to validate all username(s)
    def validate_username(self, user_to_check):
        user = Users.query.filter_by(username=user_to_check.data).first()
        if user:
            raise ValidationError('Username already exist!')

    username = StringField(label='username', validators=[
                           Length(min=4, max=30), DataRequired()])
    password = PasswordField(label='password', validators=[
                             Length(min=6), DataRequired()])
    confirm_password = PasswordField(label='confirm_password', validators=[
                                     EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    username = StringField(label='username', validators=[DataRequired()])
    password = PasswordField(label='password', validators=[DataRequired()])
    submit = SubmitField(label='Sing in')


class QuoteForm(FlaskForm):
    symbol = StringField(label='symbol', validators=[DataRequired()])
    submit = SubmitField('Quote')

    def validate_symbol(self, field):
        if lookup(field.data) == None:
            raise ValidationError("Invalid ticker.")


class Quote_to_buyForm(FlaskForm):
    symbol = StringField(label='symbol', validators=[DataRequired()])
    submit = SubmitField('Search')


class SellAsset(FlaskForm):
    company = SelectField('Select ticker', choices=[])
    shares = IntegerField('Shares')
    submit = SubmitField('Sell')

    def validate_shares(self, field):
        company = Holdings.query.filter_by(
            user_id=current_user.id, symbol=self.company.data).first()
        if field.data != None and (field.data < 1 or field.data > company.shares):
            if company.shares == 1:
                raise ValidationError(
                    "You can sell only 1 share of this stock.")
            else:
                raise ValidationError(
                    f"Number must be between 1 and {company.shares}.")


class BuyAsset(FlaskForm):
    symbol = StringField(label='Symbol', validators=[DataRequired()])
    shares = IntegerField(label='Shares')
    submit = SubmitField(label='Buy')

    def validate_shares(self, field):
        quote = lookup(self.symbol.data)
        if quote:
            max = current_user.cash // quote['price']
            if field.data != None and (field.data < 1 or field.data > max):
                raise ValidationError(
                    f"Number must be between 1 and {int(max)}.")

    def validate_symbol(self, field):
        if lookup(field.data) == None:
            raise ValidationError("Invalid ticker.")


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField(
        label='current_password', validators=[DataRequired()])
    password = PasswordField(label='password', validators=[
                             Length(min=6), DataRequired()])
    confirm_password = PasswordField(label='confirm_password', validators=[
                                     EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Change Password')


class CreateList(FlaskForm):
    name = StringField(validators=[Length(min=2, max=15), DataRequired()])
    submit = SubmitField('Create')


class EditFieldFrom(FlaskForm):
    name = SelectMultipleField('Select companies', choices=[])
    submit = SubmitField('dfdfdf')


class AddFavouriteForm(FlaskForm):
    name = HiddenField()
    list_name = SelectField('Select list', choices=[])
    submit = SubmitField('Add to list')


class SearchForm(FlaskForm):
    name = StringField(label='Input comma sepateted symbols',
                       validators=[DataRequired()])
    submit = SubmitField('Search')

    def validate_name(self, field):
        # submit = field.data
        submit = field.data.split(',')
        symbols = []
        for item in submit:
            if len(item) > 1:
                symbols.append(item.strip(" "))
        # submit = [item.strip(" ") for item in submit if len(item) > 0]
        print("submit:", symbols)
        with cf.ThreadPoolExecutor() as executor:
            responds = executor.map(lookup, symbols)
            for item in responds:
                if not item:
                    raise ValidationError("Invalid ticker.")
