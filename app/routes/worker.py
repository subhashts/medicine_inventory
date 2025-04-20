from flask import Blueprint, render_template, request, redirect, url_for,flash
from flask_login import login_required, current_user
from app.models import Worker, Medicine, Transaction
from app import db

worker_bp = Blueprint('worker', __name__, url_prefix='/worker')

@worker_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('worker/dashboard.html')

@worker_bp.route('/inventory')
@login_required
def inventory():
    medicines = Medicine.query.all()
    return render_template('worker/inventory.html', medicines=medicines)
@worker_bp.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    medicines = Medicine.query.all()
    if request.method == 'POST':
        medicine_id = request.form['medicine_id']
        quantity = int(request.form['quantity'])
        medicine = Medicine.query.get(medicine_id)
        if medicine:
            if medicine.quantity < quantity:
                flash(f"❌ Not enough stock! Only {medicine.quantity} units available.")
                return redirect(url_for('worker.sell'))
            medicine.quantity -= quantity
            db.session.commit()
            txn = Transaction(
                medicine_id=medicine.id,
                worker_id=current_user.id,
                quantity=quantity,
                type='sell',
                price=medicine.price
            )
            db.session.add(txn)
            db.session.commit()
        return redirect(url_for('worker.inventory'))
    return render_template('worker/sell.html', medicines=medicines)


@worker_bp.route('/transactions')
@login_required
def transactions():
    txns = Transaction.query.filter_by(worker_id=current_user.id).order_by(Transaction.timestamp.desc()).all()
    return render_template('worker/transactions.html', transactions=txns)
