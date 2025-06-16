from wtforms import FloatField, StringField, SubmitField, IntegerField, TextAreaField, SelectMultipleField
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
    failure_reasons = SelectMultipleField(
    "Failure Reasons",
    choices=[
        ("poor_entry", "Poor Entry"),
        ("late_exit", "Late Exit"),
        ("emotional_trade", "Emotional Trade"),
        ("news_event", "News Event"),
        ("ignored_plan", "Ignored Plan"),
        ("bad_risk", "Poor Risk Management"),
        ("slippage", "Slippage"),
    ],
    validators=[Optional()]
    )
    success_reasons = SelectMultipleField(
    "Success Reasons",
    choices=[
        ("Good Setup", "Good Setup"),
        ("Proper Risk Management", "Proper Risk Management"),
        ("Trend Alignment", "Trend Alignment"),
        ("Strong Entry Signal", "Strong Entry Signal"),
        ("Disciplined Exit", "Disciplined Exit"),
        ("News Catalyst", "News Catalyst"),
        ("Volume Surge", "Volume Surge"),
        ("Bounce Off Key Level", "Bounce Off Key Level"),
        ("Mean Reversion", "Mean Reversion"),
        ("High Conviction", "High Conviction"),
    ],
    validators=[Optional()],
    coerce=str,
    default=[]
    )


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
    failure_reasons = SelectMultipleField(
    "Failure Reasons",
    choices=[
        ("poor_entry", "Poor Entry"),
        ("late_exit", "Late Exit"),
        ("emotional_trade", "Emotional Trade"),
        ("news_event", "News Event"),
        ("ignored_plan", "Ignored Plan"),
        ("bad_risk", "Poor Risk Management"),
        ("slippage", "Slippage"),
    ],
    validators=[Optional()]
    )
    success_reasons = SelectMultipleField(
    "Success Reasons",
    choices=[
        ("Good Setup", "Good Setup"),
        ("Proper Risk Management", "Proper Risk Management"),
        ("Trend Alignment", "Trend Alignment"),
        ("Strong Entry Signal", "Strong Entry Signal"),
        ("Disciplined Exit", "Disciplined Exit"),
        ("News Catalyst", "News Catalyst"),
        ("Volume Surge", "Volume Surge"),
        ("Bounce Off Key Level", "Bounce Off Key Level"),
        ("Mean Reversion", "Mean Reversion"),
        ("High Conviction", "High Conviction"),
    ],
    coerce=str,
    default=[]
    )


class RiskCalculator(FlaskForm):
    account_value = FloatField("Total account value")
    max_risk = FloatField("Max percent of account willing to risk")
    entry_price = FloatField("Entry price")
    stop = FloatField("Stop price")
    submit = SubmitField("Submit")
