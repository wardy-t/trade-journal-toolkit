from flask_sqlalchemy import SQLAlchemy

dateformat = "%Y-%m-%d"

db = SQLAlchemy()


class Trade(db.Model):
    __tablename__ = "trades"
    ref = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=False, nullable=False)
    symbol = db.Column(db.String, nullable=False)
    num_shares = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    position_size = db.Column(db.Float, nullable=False)
    sell_date = db.Column(db.Date, nullable=True)
    sell_price = db.Column(db.Float, default=0)
    net_pnl = db.Column(db.Float, default=0)
    net_roi = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, default="")
    risk_amount = db.Column(db.Float)
    r_multiple = db.Column(db.Float)
    setup_tag = db.Column(db.String(50))
    confidence_score = db.Column(db.Integer)
    review_notes = db.Column(db.Text)
    failure_reasons = db.Column(db.String, default="")
    success_reasons = db.Column(db.String, default="")

    def to_dict(self):
        return {
            "ref": self.ref,
            "date": self.date.strftime(dateformat),
            "symbol": self.symbol,
            "num_shares": self.num_shares,
            "buy_price": self.buy_price,
            "position_size": self.position_size,
            "sell_date": self.sell_date,
            "sell_price": self.sell_price,
            "net_pnl": self.net_pnl,
            "net_roi": self.net_roi,
            "notes": self.notes,
            "risk_amount": self.risk_amount,
            "r_multiple": self.r_multiple,
            "setup_tag": self.setup_tag,
            "confidence_score": self.confidence_score,
            "review_notes": self.review_notes,
            "failure_reasons": self.failure_reasons,
            "success_reasons": self.success_reasons
        }
