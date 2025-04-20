from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Admin, Worker, Medicine, Transaction
from app import db
from datetime import date, timedelta
import random, string

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin():
    return isinstance(current_user._get_current_object(), Admin)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not is_admin(): return redirect('/')
    low_stock = Medicine.query.filter(Medicine.quantity < 10).all()
    expiring = Medicine.query.filter(Medicine.expiry_date <= date.today() + timedelta(days=30)).all()
    return render_template('admin/dashboard.html', low_stock=low_stock, expiring=expiring)

@admin_bp.route('/inventory')
@login_required
def inventory():
    if not is_admin(): return redirect('/')
    medicines = Medicine.query.all()
    return render_template('admin/inventory.html', medicines=medicines)
@admin_bp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    if not is_admin(): return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        expiry = request.form['expiry']
        price = float(request.form['price'])

        medicine = Medicine.query.filter_by(name=name).first()
        if medicine:
            medicine.quantity += quantity
            medicine.expiry_date = expiry
            medicine.price = price
        else:
            medicine = Medicine(name=name, quantity=quantity, expiry_date=expiry, price=price)
            db.session.add(medicine)
        db.session.commit()

        transaction = Transaction(medicine_id=medicine.id, worker_id=None,
                                  quantity=quantity, type='buy', price=price)
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('admin.inventory'))
    return render_template('admin/buy.html')

@admin_bp.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if not is_admin(): return redirect('/')
    medicines = Medicine.query.all()
    if request.method == 'POST':
        medicine_id = request.form['medicine_id']
        quantity = int(request.form['quantity'])
        medicine = Medicine.query.get(medicine_id)
        if medicine:
            if medicine.quantity < quantity:
                flash(f"❌ Not enough stock! Only {medicine.quantity} units available.")
                return redirect(url_for('admin.sell'))
            medicine.quantity -= quantity
            db.session.commit()
            transaction = Transaction(
                medicine_id=medicine.id,
                worker_id=None,
                quantity=quantity,
                type='sell',
                price=medicine.price
            )
            db.session.add(transaction)
            db.session.commit()
        return redirect(url_for('admin.inventory'))
    return render_template('admin/sell.html', medicines=medicines)


@admin_bp.route('/transactions')
@login_required
def transactions():
    if not is_admin(): return redirect('/')
    txns = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('admin/transactions.html', transactions=txns)

@admin_bp.route('/workers', methods=['GET', 'POST'])
@login_required
def workers():
    if not is_admin(): return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        wid = 'W' + ''.join(random.choices(string.digits, k=4))
        worker = Worker(id=wid, name=name)
        worker.set_password(password)
        db.session.add(worker)
        db.session.commit()
        flash(f"Worker Created! ID: {wid}")
    workers = Worker.query.all()
    return render_template('admin/workers.html', workers=workers)

@admin_bp.route('/delete_worker/<worker_id>')
@login_required
def delete_worker(worker_id):
    if not is_admin(): return redirect('/')
    worker = Worker.query.get(worker_id)
    if worker:
        db.session.delete(worker)
        db.session.commit()
    return redirect(url_for('admin.workers'))
@admin_bp.route('/delete_medicine/<int:medicine_id>')
@login_required
def delete_medicine(medicine_id):
    if not is_admin(): return redirect('/')
    med = Medicine.query.get(medicine_id)
    if med:
        # Delete associated transactions first
        Transaction.query.filter_by(medicine_id=med.id).delete()
        db.session.delete(med)
        db.session.commit()
    return redirect(url_for('admin.inventory'))