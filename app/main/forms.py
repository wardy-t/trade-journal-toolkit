from wtforms import FloatField, StringField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Regexp, Optional, NumberRange
from flask_wtf import FlaskForm

letterregex = "^[a-zA-Z]+$"
dateregex = "^20[0-2][0-9]-((0[1-9])|(1[0-2]))-([0-2][1-9]|3[0-1])$"


class TradeForm(FlaskForm):
    date = StringField(id="datepick", validators=[Regexp(dateregex)])
    symbol = StringField(
        "Symbol",
        validators=[
            InputRequired(),
            Regexp(letterregex, message="Invalid symbol format"),
        ],
    )
    num_shares = FloatField("No. of Shares")
    buy_price = FloatField("Buy Price")
    notes = StringField("Notes")
    risk_amount = FloatField("Risk Amount", validators=[Optional()])
    r_multiple = FloatField("R Multiple", validators=[Optional()])
    setup_tag = StringField("Setup Tag", validators=[Optional()])
    confidence_score = IntegerField("Confidence Score (1-5)", validators=[Optional(), NumberRange(min=1, max=5)])
    review_notes = TextAreaField("Review Notes", validators=[Optional()])
    submit = SubmitField("Submit")


class UpdateTradeForm(FlaskForm):
    date = StringField(id="datepick", validators=[Regexp(dateregex)])
    symbol = StringField(
        "Symbol",
        validators=[
            InputRequired(),
            Regexp(letterregex, message="Invalid symbol format"),
        ],
    )
    num_shares = FloatField("No. of Shares")
    buy_price = FloatField("Buy Price")
    sell_date = StringField(id="datepick", validators=[Optional(), Regexp(dateregex)])
    sell_price = FloatField("Sell Price", default=0, validators=[Optional()])
    notes = StringField("Notes")
    risk_amount = FloatField("Risk Amount", validators=[Optional()])
    r_multiple = FloatField("R Multiple", validators=[Optional()])
    setup_tag = StringField("Setup Tag", validators=[Optional()])
    confidence_score = IntegerField("Confidence Score (1-5)", validators=[Optional(), NumberRange(min=1, max=5)])
    review_notes = TextAreaField("Review Notes", validators=[Optional()])
    submit = SubmitField("Submit")


class RiskCalculator(FlaskForm):
    account_value = FloatField("Total account value")
    max_risk = FloatField("Max percent of account willing to risk")
    entry_price = FloatField("Entry price")
    stop = FloatField("Stop price")
    submit = SubmitField("Submit")
