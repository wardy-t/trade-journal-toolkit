from flask import render_template, flash, redirect, url_for, request
from app.models import Trade
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
from app.tools import allowed_file, csv_import
from app.main.forms import RiskCalculator, TradeForm, UpdateTradeForm
from app.main import bp
from sqlalchemy import desc, exc

dateformat = "%Y-%m-%d"


@bp.route("/", methods=["GET"])
def index():
    """
    Return the homepage.
    """
    closedtrades = Trade.query.filter(Trade.sell_price != 0.0).all()
    opentrades = Trade.query.filter(Trade.sell_price == 0.0).all()
    latesttrades = (
        Trade.query.filter(Trade.sell_price != 0.0)
        .order_by(desc(Trade.date))
        .limit(10)
        .all()
    )

    latest_labels = [trade.date.strftime(dateformat) for trade in latesttrades]
    latest_values = [trade.net_roi for trade in latesttrades]

    roidata = [trade.net_roi for trade in closedtrades]
    wins = len([win for win in roidata if win > 0])
    loses = len(roidata) - wins
    winloss_labels = ["win", "loss"]
    winloss_values = [wins, loses]


    # Filter only trades that have R-Multiple calculated
    analyzed_trades = Trade.query.filter(
        Trade.sell_price != 0.0,
        Trade.r_multiple != None
    ).all()

    total_trades = len(analyzed_trades)
    wins = len([t for t in analyzed_trades if t.r_multiple > 0])
    losses = total_trades - wins

    win_rate = round((wins / total_trades * 100), 2) if total_trades > 0 else 0
    avg_r_multiple = round(sum(t.r_multiple for t in analyzed_trades) / total_trades, 2) if total_trades > 0 else 0

    winning_r = [t.r_multiple for t in analyzed_trades if t.r_multiple > 0]
    losing_r = [t.r_multiple for t in analyzed_trades if t.r_multiple <= 0]

    avg_win_r = round(sum(winning_r) / len(winning_r), 2) if winning_r else 0
    avg_loss_r = round(sum(losing_r) / len(losing_r), 2) if losing_r else 0

    expectancy = round(((wins/total_trades) * avg_win_r) + ((losses/total_trades) * avg_loss_r), 2) if total_trades > 0 else 0

    avg_confidence = round(sum(t.confidence_score for t in analyzed_trades if t.confidence_score) / total_trades, 2) if total_trades > 0 else 0

    setup_counts = {}
    for t in analyzed_trades:
            if t.setup_tag:
                setup_counts[t.setup_tag] = setup_counts.get(t.setup_tag, 0) + 1

        # Equity Curve generation (cumulative net_pnl sum)
    equity_curve = []
    cumulative = 0

    # Sort trades by date to ensure proper time order
    sorted_trades = sorted(analyzed_trades, key=lambda x: x.date)

    for trade in sorted_trades:
        cumulative += trade.net_pnl
        equity_curve.append(round(cumulative, 2))
        
    # Also grab equity curve dates for chart
    equity_dates = [trade.date.strftime(dateformat) for trade in sorted_trades]

    # Rolling 20-trade analytics
    rolling_trades = sorted(analyzed_trades, key=lambda x: x.date)[-20:]

    rolling_total = len(rolling_trades)

    if rolling_total > 0:
        rolling_wins = len([t for t in rolling_trades if t.r_multiple > 0])
        rolling_losses = rolling_total - rolling_wins

        rolling_win_rate = round((rolling_wins / rolling_total) * 100, 2)
        rolling_avg_r = round(sum(t.r_multiple for t in rolling_trades) / rolling_total, 2)

        winning_r = [t.r_multiple for t in rolling_trades if t.r_multiple > 0]
        losing_r = [t.r_multiple for t in rolling_trades if t.r_multiple <= 0]

        avg_win_r = round(sum(winning_r) / len(winning_r), 2) if winning_r else 0
        avg_loss_r = round(sum(losing_r) / len(losing_r), 2) if losing_r else 0

        rolling_expectancy = round(
            ((rolling_wins / rolling_total) * avg_win_r) + 
            ((rolling_losses / rolling_total) * avg_loss_r), 2
        )
    else:
        rolling_win_rate = 0
        rolling_avg_r = 0
        rolling_expectancy = 0

    # Count failure reasons for trades with R-Multiple <= 0
    failure_counts = {}

    for trade in analyzed_trades:
        if trade.r_multiple <= 0 and trade.failure_reasons:
            reasons = trade.failure_reasons.split(",")
            for reason in reasons:
                reason = reason.strip()
                if reason:
                    failure_counts[reason] = failure_counts.get(reason, 0) + 1
    
        # ✅ Convert dict to lists for template rendering
    failure_labels = list(failure_counts.keys())
    failure_values = list(failure_counts.values())

    success_counts = {}

    for trade in analyzed_trades:
        if trade.r_multiple > 0 and trade.success_reasons:
            reasons = trade.success_reasons.split(",")
            for reason in reasons:
                reason = reason.strip()
                if reason:
                    success_counts[reason] = success_counts.get(reason, 0) + 1

    success_labels = list(success_counts.keys())
    success_values = list(success_counts.values())

    return render_template(
        "index.html",
        title="Trading Journal",
        winloss_labels=winloss_labels,
        winloss_values=winloss_values,
        latest_labels=latest_labels,
        latest_values=latest_values,
        opentrades=opentrades,
        closedtrades=closedtrades,
            # Pass analytics data
        total_trades=total_trades,
        win_rate=win_rate,
        avg_r_multiple=avg_r_multiple,
        expectancy=expectancy,
        avg_confidence=avg_confidence,
        setup_counts=setup_counts,
            # New equity curve data
        equity_dates=equity_dates,
        equity_curve=equity_curve,
        # Rolling analytics
        rolling_win_rate=rolling_win_rate,
        rolling_avg_r=rolling_avg_r,
        rolling_expectancy=rolling_expectancy,
        # Failure reason counts
        failure_labels=failure_labels,   
        failure_values=failure_values,
        success_labels=success_labels,
        success_values=success_values 
    )


@bp.route("/trade/add", methods=["GET", "POST"])
def add_trade():
    """
    Return existing and add new main.
    """

    form = TradeForm()

    if form.validate_on_submit():
        date = datetime.strptime(form.date.data, dateformat)
        symbol = form.symbol.data.upper()
        num_shares = form.num_shares.data
        buy_price = form.buy_price.data

        sell_date = None
        sell_price = 0.0
        position_size = round(num_shares * buy_price, 2)
        net_pnl = 0.0
        net_roi = 0.0

        record = Trade(
            date=date,
            symbol=symbol,
            num_shares=num_shares,
            buy_price=buy_price,
            sell_date=sell_date,
            sell_price=sell_price,
            position_size=position_size,
            net_pnl=net_pnl,
            net_roi=net_roi,
            notes=form.notes.data,
            risk_amount=form.risk_amount.data,
            r_multiple=form.r_multiple.data,
            setup_tag=form.setup_tag.data,
            confidence_score=form.confidence_score.data,
            review_notes=form.review_notes.data,
            failure_reasons=",".join(form.failure_reasons.data),
            success_reasons=",".join(form.success_reasons.data) 
        )

        db.session.add(record)
        db.session.commit()
        flash("Trade successfully added.", "info")

        return redirect(url_for("main.add_trade"))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    "Error in {}: {}".format(getattr(form, field).label.text, error),
                    "error",
                )

    return render_template("add_trade.html", form=form, title="Trades")


@bp.route("/trade/import", methods=["GET", "POST"])
def import_trade():
    """
    Return page used to import main from a CSV file.
    """

    if request.method == "POST":
        if "file" not in request.files or request.files["file"] == "":
            flash("No file part", "warning")
            return redirect(request.url)

        file = request.files["file"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(filename)

        csv_import(filename)
        os.remove(filename)

        flash("CSV file successfully imported.", "info")

        return render_template("import_trade.html")

    return render_template("import_trade.html")


@bp.route("/trade/update/<ref>", methods=["GET", "POST"])
def update_trade(ref):
    """
    Update an existing trade in the database.
    """

    trade = Trade.query.filter_by(ref=ref).first()
    form = UpdateTradeForm(obj=trade)

    if form.validate_on_submit():
        try:
            trade.date = datetime.strptime(form.date.data, dateformat)
            trade.symbol = form.symbol.data.upper()
            trade.num_shares = form.num_shares.data
            trade.buy_price = form.buy_price.data
            if not form.sell_date.data:
                trade.sell_date = None
            else:
                trade.sell_date = datetime.strptime(form.sell_date.data, dateformat)
            trade.sell_price = form.sell_price.data
            trade.position_size = round(form.num_shares.data * form.buy_price.data, 2)
            trade.notes = form.notes.data
            trade.risk_amount = form.risk_amount.data
            trade.r_multiple = form.r_multiple.data
            trade.setup_tag = form.setup_tag.data
            trade.confidence_score = form.confidence_score.data
            trade.review_notes = form.review_notes.data
            trade.failure_reasons = ",".join(form.failure_reasons.data)
            trade.success_reasons = ",".join(form.success_reasons.data)

            if form.sell_price.data == 0:
                trade.net_pnl = 0
                trade.net_roi = 0

            else:
                trade.net_pnl = round(
                    (form.num_shares.data * form.sell_price.data) - trade.position_size,
                    2,
                )
                trade.net_roi = round(trade.net_pnl / trade.position_size * 100, 2)

            db.session.add(trade)
            db.session.commit()
            flash("Trade updated successfully.", "success")

        except exc.SQLAlchemyError:
            db.session.rollback()
            flash("Error updating trade.", "danger")

    return render_template("update_trade.html", form=form)


@bp.route("/trade/delete/<ref>", methods=["Delete"])
def delete_trade(ref):
    """
    Update an exiting trade in the database.
    """

    trade = Trade.query.get(ref)

    if trade:
        db.session.delete(trade)
        db.session.commit()
        # flash("Delete successful.", "danger")
        return "", 204

    else:
        # flash("Error deleting trade.", "danger")
        return "Trade not found", 404

    # return redirect(url_for("main.index"))


@bp.route("/risk", methods=["GET", "POST"])
def risk_calculator():
    """
    Risk calculator
    """

    form = RiskCalculator()
    risk = {}

    if request.method == "POST":
        if form.validate_on_submit():
            account_value = form.account_value.data
            max_risk = form.max_risk.data
            entry_price = form.entry_price.data
            stop = form.stop.data

            account_risk = account_value / 100 * max_risk
            trade_risk = entry_price - stop

            risk["risk_per_share"] = round(trade_risk, 2)
            risk["num_shares"] = round(account_risk / trade_risk, 2)
            risk["position_size"] = round(risk["num_shares"] * entry_price, 2)
            risk["risk_per_share_percent"] = round(
                (risk["risk_per_share"] / entry_price) * 100, 2
            )
            risk["risk_account_value"] = round(
                risk["num_shares"] * risk["risk_per_share"], 2
            )

        return render_template("risk_calculator.html", form=form, risk=risk)

    return render_template("risk_calculator.html", form=form, risk=risk)
