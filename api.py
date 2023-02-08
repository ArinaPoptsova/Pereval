import datetime
import json

from flask import Flask, request, jsonify
from marshmallow import ValidationError
# from psycopg2 import IntegrityError
# from psycopg2 import DataError
from werkzeug.exceptions import BadRequest

from dataclass import Pereval
from sqlalchemy.exc import OperationalError, DataError, IntegrityError, InternalError
from schemas import validate_email

app = Flask(__name__)

def add_and_get_image(pereval, data, i):
    try:
        pereval.add_image(data['images'][i]['title'], (data['images'][i]['data']).encode('utf-8'))
    except:
        img = None
    else:
        img = pereval.get_image(data['images'][i]['title'])
    return img

def get_image(data, i):
    try:
        img = {'title': data['images'][i]['title'], 'img': data['images'][i]['data']}
    except:
        img = None
    return img

@app.route('/submitData/create/', methods=['POST'])
def submitData():
    try:
        pereval = Pereval()
        data = request.get_json()
        if not pereval.is_user_exist(data['user']['email']):
            pereval.add_user(data['user']['email'], data['user']['fam'], data['user']['name'], data['user']['phone'],
                            data['user']['otc'])
        pereval.add_coords(data['coords']['latitude'], data['coords']['longitude'], data['coords']['height'])

        if data['images']:
            img_1 = add_and_get_image(pereval, data, 0)
            img_2 = add_and_get_image(pereval, data, 1)
            img_3 = add_and_get_image(pereval, data, 2)

            pereval.add_pereval_images(img_1.id if img_1 else None,
                                    img_2.id if img_2 else None,
                                    img_3.id if img_3 else None)
            images_id = pereval.get_images_id(img_1.id if img_1 else None)
        else:
            images_id = None
        pereval.add_level(data['level']['winter'], data['level']['summer'],
                            data['level']['autumn'], data['level']['spring'])

        validate_email(data['user']['email'])

        user_id = pereval.get_user_id(data['user']['email'])
        coords_id = pereval.get_coords_id(data['coords']['latitude'], data['coords']['longitude'],
                                            data['coords']['height'])
        level_id = pereval.get_level_id(data['level']['winter'], data['level']['summer'],
                                        data['level']['autumn'], data['level']['spring'])

        pereval.add_pereval(date_added=datetime.datetime.utcnow(), user_id=user_id, coords_id=coords_id,
                            beautyTitle=data['beauty_title'], title=data['title'], other_titles=data['other_titles'],
                            connect=data['connect'], add_time=data['add_time'], images_id=images_id,
                            level_id=level_id)
    except OperationalError:
        response = {'status': 500, 'message': 'Ошибка подключения к БД', 'id': None}
    except IntegrityError:
        response = {'status': 400, 'message': 'Пропущены обязательные поля', 'id': None}
    except InternalError:
        response = {'status': 400, 'message': 'Данное поле должно быть уникальным', 'id': None}
    # except TypeError:
    #     response = {'status': 400, 'message': 'Неверно введённые данные', 'id': None}
    # except ValidationError:
    #     response = {'status': 400, 'message': 'Неверно введённые данные', 'id': None}
    # except DataError:
    #     response = {'status': 400, 'message': 'Неверно введённые данные', 'id': None}
    else:
        pereval_id = pereval.get_pereval_id(images_id)
        response = {'status': 200, 'message': None, 'id': pereval_id}
    finally:
        return json.dumps(response, ensure_ascii=False)


@app.route('/submitData/<int:id>/', methods=['GET'])
def getPereval(id):
    pereval = Pereval()
    data = json.dumps(pereval.get_pereval_by_id(id))
    return data


@app.route('/submitData/<int:id>/', methods=['PATCH'])
def changeData(id):
    pereval = Pereval()
    if pereval.is_status_new(id):
        try:
            pereval_data = pereval.get_pereval_by_id(id)
            coords_id = pereval.get_coords_id(pereval_data['coords']['latitude'],
                                              pereval_data['coords']['longitude'], pereval_data['coords']['height'])
            if pereval_data['images'][0]['title']:
                img_1_id = pereval.get_image(pereval_data['images'][0]['title']).id
                images_id = pereval.get_images_id(img_1_id)
            else:
                img_1_id = None
                images_id = None

            if pereval_data['images'][1]['title']:
                img_2_id = pereval.get_image(pereval_data['images'][1]['title']).id
            else:
                img_2_id = None
            if pereval_data['images'][2]['title']:
                img_3_id = pereval.get_image(pereval_data['images'][2]['title']).id
            else:
                img_3_id = None


            if pereval_data['level']['winter'] or pereval_data['level']['summer'] or \
                    pereval_data['level']['autumn'] or pereval_data['level']['spring']:
                level_id = pereval.get_level_id(pereval_data['level']['winter'], pereval_data['level']['summer'],
                                            pereval_data['level']['autumn'], pereval_data['level']['spring'])
            else:
                level_id = None


            data = request.get_json()
            pereval.change_coords(coords_id, data['coords']['latitude'],
                                              data['coords']['longitude'], data['coords']['height'])
            if data['level']:
                if level_id:
                    pereval.change_level(level_id, data['level']['winter'], data['level']['summer'],
                                    data['level']['autumn'], data['level']['spring'])
                else:
                    pereval.add_level(data['level']['winter'], data['level']['summer'],
                                data['level']['autumn'], data['level']['spring'])
                    level_id = pereval.get_level_id(data['level']['winter'], data['level']['summer'],
                                                    data['level']['autumn'], data['level']['spring'])
            else:
                level_id = None

            if data['images']:
                if images_id:
                    # img_1 = get_image(data, 0)
                    img_2 = get_image(data, 1)
                    img_3 = get_image(data, 2)
                    pereval.change_images(images_id, img_1_id, data['images'][0]['title'],
                                    data['images'][0]['data'].encode('utf-8'),
                                    img_2_id if img_2 else None,
                                    img_2['title'] if img_2 else None,
                                    img_2['img'].encode('utf-8') if img_2 else None,
                                    img_3_id if img_3 else None,
                                    img_3['title'] if img_3 else None,
                                    img_3['img'].encode('utf-8') if img_3 else None)
                else:
                    img_1 = add_and_get_image(pereval, data, 0)
                    img_2 = add_and_get_image(pereval, data, 1)
                    img_3 = add_and_get_image(pereval, data, 2)

                    pereval.add_pereval_images(img_1.id,
                                               img_2.id if img_2 else None,
                                               img_3.id if img_3 else None)
                    images_id = pereval.get_images_id(img_1.id)
            else:
                images_id = None

            pereval.change_pereval(id=id, date_added=pereval.get_date_added(id), beautyTitle=data['beauty_title'],
                                   title=data['title'], other_titles=data['other_titles'], connect=data['connect'],
                                   coords_id=coords_id, level_id=level_id, images_id=images_id)
        except TypeError:
            response = {'state': 0, 'message': 'Неверно введённые данные'}
        except DataError:
            response = {'state': 0, 'message': 'Неверно введённые данные'}
        except IntegrityError:
            response = {'state': 0, 'message': 'Пропущены обязательные поля'}
        # except KeyError:
        #     response = {'state': 0, 'message': 'Объект не существвует'}
        except InternalError:
            response = {'state': 0, 'message': 'Данное поле должно быть уникальным'}
        except OperationalError:
            response = {'state': 0, 'message': 'Ошибка подключения к БД'}
        else:
            response = {'state': 1, 'message': ''}
        return json.dumps(response, ensure_ascii=False)

@app.route('/submitData/', methods=['GET'])
def getUsersPereval():
    user_email = request.args.get('user_email')
    pereval = Pereval()
    data = json.dumps(pereval.get_users_perevals(user_email))
    return data


# "{\"beauty_title\": \"New_Beauty_Pereval\", \"title\": \"Pereval\", \"other_titles\": \"New_Pereval\", \"connect\": \"\", \"add_time\": \"2022-12-15 15:35:20\", \"user\": {\"email\": \"arina.poptsova@yandex.ru\", \"fam\": \"Poptsova\", \"name\": \"Arina\", \"otc\": \"Aleksandrovna\", \"phone\": \"89555555555\"}, \"coords\":{ \"latitude\": \"63.1532\", \"longitude\": \"10.4728\", \"height\": \"2100\"}, \"level\":{\"winter\": \"\", \"summer\": \"1А\", \"autumn\": \"1А\", \"spring\": \"\"}, \"images\": [{\"data\": \b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\', \"spring\": \"0img\"}]}"

# r"{"beauty_title": "New_Beauty_Pereval", "title": "Pereval", "other_titles": "New_Pereval", "connect": "", "add_time": "2022-12-15 15:35:20", "user": {"email": "arina.poptsova@yandex.ru", "fam": "Poptsova", "name": "Arina", "otc": "Aleksandrovna", "phone": "89555555555"}, "coords":{"latitude": "63.1532", "longitude": "10.4728", "height": "2100"}, "level":{"winter": "", "summer": "1А", "autumn": "1А", "spring": ""}, "images": [{"data": b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", "spring": "0img"}]}"

# "{\"beauty_title\": \"New_Beauty_Pereval\", \"title\": \"Pereval\", \"other_titles\": \"New_Pereval\", \"connect\": \"\", \"add_time\": \"2022-12-15 15:35:20\", \"user\": {\"email\": \"arina.poptsova@yandex.ru\", \"fam\": \"Poptsova\", \"name\": \"Arina\", \"otc\": \"Aleksandrovna\", \"phone\": \"89555555555\"}, \"coords\":{ \"latitude\": \"63.1532\", \"longitude\": \"10.4728\", \"height\": \"2100\"}, \"level\":{\"winter\": \"\", \"summer\": \"1А\", \"autumn\": \"1А\", \"spring\": \"\"}, \"images\": [{\"data\": "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", \"spring\": \"0img\"}]}"

if __name__ == '__main__':
    app.run(debug=True)
