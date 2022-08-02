from flask import Flask, render_template, redirect, abort, url_for, request
from flask_login import LoginManager, login_required, \
    login_user, current_user, logout_user
import json
from data import db_session
from data.admins import Admins
from data.tasks import Task
from data.restaurants import Restaurant
from data.restaurant_types import RestaurantTypes
from forms.planform import PlannerForm
from forms.add_restaurant import AddRestaurantForm
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'nnwllknwthscd'
db_session.global_init("db/cafe27.db")
db_sess = db_session.create_session()
# login_manager = LoginManager()
# login_manager.init_app(app)


# @login_manager.user_loader
# def load_user(user_id):
   #  db_sess = db_session.create_session()
    #  return db_sess.query(Admins).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Dashboard')


@app.route('/all_tasks')
def all_tasks():
    tasks = db_sess.query(Task).all()
    return render_template('all_tasks.html', title='Планировщик', tasks=tasks)


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = db_sess.query(Task).filter(Task.id == task_id).one()
    db_sess.delete(task)
    db_sess.commit()
    return redirect('../../all_tasks')


@app.route('/planner')
def planner():
    restaurants = db_sess.query(Restaurant).all()
    return render_template('planner.html', title='Планировщик', restaurants=restaurants)


@app.route('/planform/<int:rest_id>', methods=["GET", "POST"])
def planform(rest_id):
    form = PlannerForm()
    if form.validate_on_submit():
        date = datetime.datetime(year=form.date.data.year,
                                 month=form.date.data.month,
                                 day=form.date.data.day,
                                 hour=form.time.data.hour,
                                 minute=form.time.data.minute)
        if date > datetime.datetime.now():
            new_task = Task(
                task_type='restaurant',
                item_id=rest_id,
                datetime=date
            )
            db_sess.add(new_task)
            db_sess.commit()
        else:
            return render_template('planform.html', form=form)
        return redirect('/../../all_tasks')
    return render_template('planform.html', form=form)


@app.route('/user_filter', methods=["GET", "POST"])
def user_filter():
    categories = db_sess.query(RestaurantTypes).filter(RestaurantTypes.default == 0).all()
    if request.method == 'GET':
        return render_template('user_filter.html', categories=categories)
    elif request.method == 'POST':
        ids = list(map(int, list(dict(request.form.to_dict()).keys())))
        print(list(ids))
        for elem in categories:
            if elem.id in ids:
                elem.only_vip = 0
            else:
                elem.only_vip = 1
            db_sess.commit()
        return render_template('user_filter.html', categories=categories)


@app.route('/add_restaurant', methods=['GET', 'POST'])
def add_restaurant():
    form = AddRestaurantForm()
    if form.validate_on_submit():
        return render_template('add_restaurant.html', form=form)
    return render_template('add_restaurant.html', form=form)


def main():
    app.run(host="127.0.0.1", port=5000)


if __name__ == '__main__':
    main()
