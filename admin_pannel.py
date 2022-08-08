from flask import Flask, render_template, redirect, request
import json
import requests
from data import db_session
from data.tasks import Task
from data.restaurants import Restaurant
from data.restaurant_types import RestaurantTypes
from data.payments import Payment
from data.users import User
from data.blacklist import Blacklist
from data.posts import Posts
from data.banners import Banner
from data.polls import Poll
from forms.planform import PlannerForm
from forms.add_restaurant import AddRestaurantForm
from forms.bad_words_form import BadWordsForm
from forms.spam_form import SpamForm
from forms.vip_form import VIPForm
from forms.add_post import PostForm
from forms.add_type import TypeForm
from forms.add_poll import PollForm
from forms.add_banner import BannerForm
from forms.edit_post import EditPostForm
from forms.edit_restaurant import EditRestaurantForm
import datetime
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nnwllknwthscd'
db_session.global_init("db/cafe27.db")
db_sess = db_session.create_session()
P_TOKEN = ""
with open('json/messages.json') as json_d:
    json_keys_data = json.load(json_d)
API_KEY = json_keys_data['API_keys']['translator']
folder_id = json_keys_data['API_keys']['folder_id']
organization_api = json_keys_data['API_keys']['organization_search']
search_api_server = json_keys_data['API_keys']['search_api_server']
translate_api_server = json_keys_data['API_keys']["translate_api_server"]
map_api_server = json_keys_data['API_keys']["map_api_server"]
target_language = 'en'


def process_images(images):
    filenames = []
    for im in images:
        im2 = im.filename
        nm = secrets.token_urlsafe(16)
        if im2.rsplit('.', 1)[1].lower() in ('jpg', 'jpeg'):
            im.save(os.path.join(f'static/img/{nm}.jpg'))
            filenames.append(f'static/img/{nm}.jpg')
        elif im2.rsplit('.', 1)[1].lower() == 'png':
            im.save(os.path.join(f'static/img/{nm}.png'))
            filenames.append(f'static/img/{nm}.png')
        else:
            return 'error1'

    filenames = ';'.join(filenames)
    return filenames


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Dashboard',
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/all_tasks')
def all_tasks():
    tasks = db_sess.query(Task).filter(Task.task_type.notlike(f"%del%"))
    return render_template('all_tasks.html', title='Планировщик', tasks=tasks,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = db_sess.query(Task).filter(Task.id == task_id).one()
    del_task = Task(
        task_type=f'del_{task.task_type}_{task.item_id}',
        item_id=10000000,
        datetime=datetime.datetime.now(),
        in_work=0
    )
    if task.task_type == 'poll':
        poll_to_delete = db_sess.query(Poll).filter(Poll.id == task.item_id).one()
        db_sess.delete(poll_to_delete)
    db_sess.add(del_task)
    db_sess.delete(task)
    db_sess.commit()
    return redirect('../../all_tasks')


@app.route('/planner')
def planner():
    restaurants = db_sess.query(Restaurant).all()
    return render_template('planner.html', title='Планировщик', restaurants=restaurants,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/planform/<int:rest_id>', methods=["GET", "POST"])
def planform(rest_id):
    form = PlannerForm()
    if form.validate_on_submit():
        date = datetime.datetime(year=form.date.data.year,
                                 month=form.date.data.month,
                                 day=form.date.data.day,
                                 hour=form.time.data.hour,
                                 minute=form.time.data.minute)
        if date > datetime.datetime.now() + datetime.timedelta(hours=3):
            new_task = Task(
                task_type='restaurant',
                item_id=rest_id,
                datetime=date,
                in_work=0
            )
            db_sess.add(new_task)
            db_sess.commit()
        else:
            return render_template('planform.html', form=form,
                                   datetime=datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
        return redirect('/../../all_tasks')
    return render_template('planform.html', form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/user_filter', methods=["GET", "POST"])
def user_filter():
    categories = db_sess.query(RestaurantTypes).filter(RestaurantTypes.default == 0).all()
    if request.method == 'GET':
        return render_template('user_filter.html', categories=categories)
    elif request.method == 'POST':
        ids = list(map(int, list(dict(request.form.to_dict()).keys())))
        for elem in categories:
            if elem.id in ids:
                elem.only_vip = 0
            else:
                elem.only_vip = 1
            db_sess.commit()
        return render_template('user_filter.html', categories=categories,
                               datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime(
                                   "%d.%m.%y %H:%M"))


@app.route('/add_restaurant', methods=['GET', 'POST'])
def add_restaurant():
    form = AddRestaurantForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        address = form.address.data
        average = form.average.data
        types = form.types.data
        operating = form.operating.data
        media = form.media.raw_data[:8]
        on_maps = form.on_maps.data
        if on_maps:
            search_params = {
                "apikey": organization_api,
                "text": f"{name} {address}",
                "lang": "ru_RU",
                "type": "biz",
                "results": '1'
            }

            rest_response = requests.get(search_api_server, params=search_params).json()
            try:
                address = ', '.join(
                    rest_response['features'][0]['properties']['CompanyMetaData']['address'].split(', ')[1:])
            except (KeyError, IndexError):
                address = address
            try:
                working_hours = rest_response['features'][0]['properties']['CompanyMetaData']['Hours']['text']
            except (KeyError, IndexError):
                working_hours = operating
            try:
                phone = rest_response['features'][0]['properties']['CompanyMetaData']['Phones'][0]['formatted']
            except (KeyError, IndexError):
                phone = ''
            try:
                name = rest_response['features'][0]['properties']['name']
            except (KeyError, IndexError):
                name = name
            coordinates = ','.join(map(str, [rest_response['features'][0]['geometry']['coordinates'][1],
                                             rest_response['features'][0]['geometry']['coordinates'][0]]))
        else:
            search_params = {
                "apikey": organization_api,
                "text": f"{address}",
                "lang": "ru_RU",
                "results": '1'
            }
            rest_response = requests.get(search_api_server, params=search_params).json()
            coordinates = ','.join(map(str, [rest_response['features'][0]['geometry']['coordinates'][1],
                                             rest_response['features'][0]['geometry']['coordinates'][0]]))
            phone = ''
            address = address
            working_hours = operating
            name = name
        texts = [name,
                 description,
                 address,
                 working_hours,
                 ]
        body = {
            "targetLanguageCode": target_language,
            "texts": texts,
            "folderId": folder_id,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key {0}".format(API_KEY)
        }
        response = requests.post(translate_api_server,
                                 json=body,
                                 headers=headers
                                 ).json()
        name_en = response['translations'][0]['text']
        description_en = response['translations'][1]['text']
        address_en = response['translations'][2]['text']
        working_hours_en = response['translations'][3]['text']

        images = process_images(media).split(';')
        images.insert(0, images[0])

        types = db_sess.query(RestaurantTypes).filter(RestaurantTypes.type_name.in_(types)).all()
        types = ', '.join(map(lambda x: str(x.id), types))
        new_rest = Restaurant(
            name=name,
            address=address,
            coordinates=coordinates,
            description=description,
            phone=phone,
            working_hours=working_hours,
            vip_owner=0,
            confirmed=1,
            name_en=name_en,
            description_en=description_en,
            working_hours_en=working_hours_en,
            address_en=address_en,
            media=';'.join(images),
            average_price=average,
            type=types,
        )
        db_sess.add(new_rest)
        db_sess.commit()
        return render_template('index.html', form=form, datetime=datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
    return render_template('add_restaurant.html', form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/statistics')
def statistics():
    with open('json/messages.json') as json_b:
        json_block_data = json.load(json_b)
    stats = [['Статистика бота', json_block_data['links']['bot_stat']],
             ['Статистика канала (RU)', json_block_data['links']['channel_stat_ru']],
             ['Статистика канала (EN)', json_block_data['links']['channel_stat_en']]]
    return render_template('statistics.html', stats=stats,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/invoice')
def invoice():
    payments = db_sess.query(Payment).all()
    ids = list(map(lambda x: x.user, payments))
    users = db_sess.query(User).filter(User.id.in_(ids)).all()
    users = list(map(lambda x: x.username, users))
    return render_template('invoice.html', payments=payments, users=users,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/bad_words', methods=['GET', 'POST'])
def bad_words():
    form = BadWordsForm()
    if form.validate_on_submit():
        with open('json/messages.json') as json_b:
            json_block_data = json.load(json_b)
            json_block_data['punishments']['ban_words']['timeout'] = form.lenght.data
            json_block_data['ban_words'] = form.words.data.split(';')
        with open('json/messages.json', 'w') as json_b:
            json.dump(json_block_data, json_b)
        return redirect('/bad_words')
    with open('json/messages.json') as json_b:
        json_block_data = json.load(json_b)
    block_l = json_block_data['punishments']['ban_words']['timeout']
    words = ';'.join(json_block_data['ban_words'])
    form.words.data = words
    form.lenght.data = block_l
    banned_users = db_sess.query(Blacklist).filter(Blacklist.reason
                                                   == json_block_data['punishments']['ban_words']['name']).all()
    return render_template('bad_words.html', form=form, banned_users=banned_users,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/spam', methods=['GET', 'POST'])
def spam():
    form = SpamForm()
    if form.validate_on_submit():
        with open('json/messages.json') as json_b:
            json_block_data = json.load(json_b)
            json_block_data['punishments']['spam']['timeout'] = form.lenght.data
            json_block_data['punishments']['spam']['number_of_messages'] = form.mes.data
        with open('json/messages.json', 'w') as json_b:
            json.dump(json_block_data, json_b)
        return redirect('/spam')
    with open('json/messages.json') as json_b:
        json_block_data = json.load(json_b)
    block_l = json_block_data['punishments']['spam']['timeout']
    mes = json_block_data['punishments']['spam']['number_of_messages']
    form.mes.data = mes
    form.lenght.data = block_l
    banned_users = db_sess.query(Blacklist).filter(Blacklist.reason
                                                   == json_block_data['punishments']['spam']['name']).all()
    return render_template('spam.html', form=form, banned_users=banned_users,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/all_posts')
def all_posts():
    posts = db_sess.query(Posts).all()
    return render_template('all_posts.html', posts=posts,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/chat_statistics')
def chat_statistics():
    with open('json/messages.json') as json_b:
        json_block_data = json.load(json_b)
    stats = [['Статистика чата', json_block_data['links']['chat_stat']]]
    return render_template('statistics.html', stats=stats,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/moderator', methods=['GET', 'POST'])
def moderator():
    form = VIPForm()
    if form.validate_on_submit():
        with open('json/messages.json') as json_b:
            json_block_data = json.load(json_b)
            json_block_data['payments']['VIP'] = form.price.data * 100
        with open('json/messages.json', 'w') as json_b:
            json.dump(json_block_data, json_b)
        return redirect('moderator')
    sp = []
    with open('json/messages.json') as json_b:
        json_block_data = json.load(json_b)
    for elem in json_block_data['messages']['ru']:
        sp.append((elem, json_block_data['messages']['ru'][elem]))
    for elem in json_block_data['messages']['en']:
        sp.append((elem, json_block_data['messages']['en'][elem]))
    form.price.data = json_block_data['payments']['VIP'] // 100
    return render_template('moderator.html', messages=sp, form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/all_restaurants')
def all_restaurants():
    restaurants = db_sess.query(Restaurant).all()
    return render_template('all_restaurants.html', restaurants=restaurants,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/all_types')
def all_types():
    types = db_sess.query(RestaurantTypes).all()
    return render_template('all_types.html', types=types,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/all_banners')
def all_banners():
    banners = db_sess.query(Banner).all()
    return render_template('all_banners.html', banners=banners,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/all_polls')
def all_polls():
    polls = db_sess.query(Poll).all()
    return render_template('all_polls.html', polls=polls,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/all_users')
def all_users():
    users = db_sess.query(User).all()
    return render_template('all_users.html', users=users,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/planpost/<int:post_id>', methods=['GET', 'POST'])
def planpost(post_id):
    form = PlannerForm()
    if form.validate_on_submit():
        date = datetime.datetime(year=form.date.data.year,
                                 month=form.date.data.month,
                                 day=form.date.data.day,
                                 hour=form.time.data.hour,
                                 minute=form.time.data.minute)
        if date > datetime.datetime.now() + datetime.timedelta(hours=3):
            new_task = Task(
                task_type='post',
                item_id=post_id,
                datetime=date,
                in_work=0
            )
            db_sess.add(new_task)
            db_sess.commit()
        else:
            return render_template('planform.html', form=form,
                                   datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime(
                                       "%d.%m.%y %H:%M"))
        return redirect('/../../all_posts')
    return render_template('planform.html', form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        header = form.header.data
        text = form.text.data
        media = form.media.raw_data
        try:
            images = process_images(media)
        except IndexError:
            images = ''
        new_post = Posts(
            header=header,
            text=text,
            media=images
        )
        db_sess.add(new_post)
        db_sess.commit()
        return redirect('/all_posts')
    return render_template('add_post.html', form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    form = TypeForm()
    if form.validate_on_submit():
        name = form.name.data
        name_en = form.english_name.data
        new_type = RestaurantTypes(
            type_name=name,
            only_vip=0,
            type_name_en=name_en,
            default=0
        )
        db_sess.add(new_type)
        db_sess.commit()
        return redirect('/all_types')
    return render_template('add_type.html', form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/add_poll', methods=['GET', 'POST'])
def add_poll():
    form = PollForm()
    if form.validate_on_submit():
        date = datetime.datetime(year=form.publication_date.data.year,
                                 month=form.publication_date.data.month,
                                 day=form.publication_date.data.day,
                                 hour=form.publication_time.data.hour,
                                 minute=form.publication_time.data.minute)
        if date > datetime.datetime.now() + datetime.timedelta(hours=3):
            header = form.name.data
            variants = form.variants.data
            is_anon = form.is_anon.data
            new_poll = Poll(
                header=header,
                variants=variants,
                datetime=date,
                is_anon=is_anon
            )
            db_sess.add(new_poll)
            db_sess.commit()
            poll = db_sess.query(Poll).filter(Poll.datetime == date, Poll.header == header).one()
            new_task = Task(
                task_type='poll',
                item_id=poll.id,
                datetime=poll.datetime,
                in_work=0
            )
            db_sess.add(new_task)
            db_sess.commit()
            return redirect('/all_tasks')
        return render_template('add_poll.html', form=form,
                               datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime(
                                   "%d.%m.%y %H:%M"))
    return render_template('add_poll.html', form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/add_banner', methods=['GET', 'POST'])
def add_banner():
    form = BannerForm()
    if form.validate_on_submit():
        date = datetime.datetime(year=form.publication_date.data.year,
                                 month=form.publication_date.data.month,
                                 day=form.publication_date.data.day,
                                 hour=form.publication_time.data.hour,
                                 minute=form.publication_time.data.minute)
        if date > datetime.datetime.now() + datetime.timedelta(hours=3):
            text = form.text.data
            name = form.name.data
            image = form.image.raw_data
            try:
                image = process_images(image)
            except IndexError:
                image = None
            new_banner = Banner(
                name=name,
                text=text,
                image=image,
                datetime=date
            )
            db_sess.add(new_banner)
            db_sess.commit()
            banner = db_sess.query(Banner).filter(Banner.datetime == date, Banner.text == text,
                                                  Banner.name == name).all()[0]
            new_task = Task(
                task_type='banner',
                item_id=banner.id,
                datetime=banner.datetime,
                in_work=0
            )
            db_sess.add(new_task)
            db_sess.commit()
            return redirect('/all_tasks')
        return render_template('add_banner.html', form=form,
                               datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime(
                                   "%d.%m.%y %H:%M"))
    return render_template('add_banner.html', form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = db_sess.query(Posts).filter(Posts.id == post_id).one()
    if post.media is not None:
        images = post.media.split(';')
    else:
        images = ['']

    form = EditPostForm()
    if form.validate_on_submit():
        post.header = form.header.data
        post.text = form.text.data
        new_images = form.current_media.data.split(';')
        media = form.media.raw_data
        a = set(images)
        b = set(new_images)
        pictures_remains = list(a & b)

        try:
            images = process_images(media)
            pictures_remains.extend(images.split(';'))
        except IndexError:
            pass
        while '' in pictures_remains:
            pictures_remains.remove('')
        if len(pictures_remains) != 0:
            post.media = ';'.join(pictures_remains)
        else:
            post.media = None
        db_sess.commit()
        return redirect('/all_posts')
    sp = []
    for elem in images:
        if elem != '':
            sp.append('/'.join(elem.split('/')[1:]))
    form.header.data = post.header
    form.text.data = post.text
    if images != ['']:
        form.current_media.data = post.media
    return render_template('edit_post.html', form=form, images=sp,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/edit_category/<int:type_id>', methods=['GET', 'POST'])
def edit_category(type_id):
    form = TypeForm()
    category = db_sess.query(RestaurantTypes).filter(RestaurantTypes.id == type_id).one()
    if form.validate_on_submit():
        category.type_name = form.name.data
        category.type_name_en = form.english_name.data
        db_sess.commit()
        return redirect('/all_types')
    form.name.data = category.type_name
    form.english_name.data = category.type_name_en
    return render_template('add_type.html', form=form,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/edit_restaurant/<int:rest_id>', methods=['GET', 'POST'])
def edit_restaurant(rest_id):
    restaurant = db_sess.query(Restaurant).filter(Restaurant.id == rest_id).one()
    form = EditRestaurantForm()
    images = restaurant.media.split(';')
    if form.validate_on_submit():
        restaurant.name = form.name.data
        restaurant.name_en = form.name_en.data
        restaurant.description = form.description.data
        restaurant.description_en = form.description_en.data
        restaurant.address = form.address.data
        restaurant.address_en = form.address_en.data
        restaurant.average_price = form.average.data
        types = form.types.data
        types = db_sess.query(RestaurantTypes).filter(RestaurantTypes.type_name.in_(types)).all()
        types = ', '.join(map(lambda x: str(x.id), types))
        restaurant.type = types
        new_images = form.current_media.data.split(';')
        media = form.media.raw_data
        new_main_photo = form.new_main_pic.raw_data
        a = set(images)
        b = set(new_images)
        pictures_remains = list(a & b)
        if images[0] in pictures_remains and not (new_main_photo[0].filename == '' and len(new_main_photo) == 1):
            pictures_remains.remove(images[0])
            if images[0] in pictures_remains:
                pictures_remains.remove(images[0])
            new_photo = process_images(new_main_photo)
            pictures_remains.insert(0, new_photo)
            pictures_remains.insert(0, new_photo)
        else:
            while images[0] in pictures_remains:
                pictures_remains.remove(images[0])
            pictures_remains.insert(0, images[0])
            pictures_remains.insert(0, images[0])
        if not (len(media) == 1 and media[0].filename == ''):
            new_media = process_images(media).split(';')
            pictures_remains.extend(new_media)
        while '' in pictures_remains:
            pictures_remains.remove('')
        final_pictures = ';'.join(pictures_remains[:8])
        restaurant.media = final_pictures
        if form.change_geopos:
            search_params = {
                "apikey": organization_api,
                "text": f"{form.address.data}",
                "lang": "ru_RU",
                "results": '1'
            }
            rest_response = requests.get(search_api_server, params=search_params).json()
            coordinates = ','.join(map(str, [rest_response['features'][0]['geometry']['coordinates'][1],
                                             rest_response['features'][0]['geometry']['coordinates'][0]]))
            restaurant.coordinates = coordinates
        db_sess.commit()
        return redirect('/all_restaurants')
    sp = []
    for elem in images:
        if elem != '':
            sp.append('/'.join(elem.split('/')[1:]))
    form.name.data = restaurant.name
    form.description.data = restaurant.description
    form.address.data = restaurant.address
    form.average.data = restaurant.average_price
    form.current_media.data = restaurant.media
    form.operating.data = restaurant.working_hours
    form.name_en.data = restaurant.name_en
    form.description_en.data = restaurant.description_en
    form.address_en.data = restaurant.address_en
    form.operating_en.data = restaurant.working_hours_en
    return render_template('edit_restaurant.html', form=form, images=sp,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/moder/<int:user_id>')
def moder(user_id):
    user = db_sess.query(User).filter(User.id == user_id).one()
    user.moderator = 1
    db_sess.commit()
    return redirect('/all_users')


@app.route('/not_moder/<int:user_id>')
def not_moder(user_id):
    user = db_sess.query(User).filter(User.id == user_id).one()
    user.moderator = 0
    db_sess.commit()
    return redirect('/all_users')


@app.route('/one_poll/<int:poll_id>')
def one_poll(poll_id):
    poll = db_sess.query(Poll).filter(Poll.id == poll_id).one()
    try:
        total_answers = sum(map(int, poll.answers.split(';')))
    except AttributeError:
        return redirect('../../all_polls')
    variants = []
    all_variants = poll.variants.split(';')
    all_totals = poll.answers.split(';')
    number_of_variants = len(poll.variants.split(';'))
    for i in range(number_of_variants):
        try:
            variants.append([i + 1, all_variants[i], round((int(all_totals[i]) / total_answers) * 100)])
        except ZeroDivisionError:
            variants.append([i + 1, all_variants[i], 0])
    return render_template('poll.html', variants=variants,
                           datetime=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m.%y %H:%M"))


@app.route('/unblock_user/<int:user_id>')
def unblock_user(user_id):
    user_blacklist = db_sess.query(Blacklist).filter(Blacklist.telegram_id == user_id).all()[0]
    db_sess.delete(user_blacklist)
    db_sess.commit()
    return redirect('/../all_users')


def main():
    app.run(host="0.0.0.0")


if __name__ == '__main__':
    main()
