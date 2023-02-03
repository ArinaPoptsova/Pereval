import datetime
import json

from flask import Flask
from .dataclass import Pereval
from sqlalchemy.exc import OperationalError


app = Flask(__name__)


@app.route('/pereval/create/', methods=['POST'])
def submitData(json_data):
    try:
        pereval = Pereval()
        data = json.loads(json_data)
        pereval.add_user(data['user']['email'], data['user']['fam'], data['user']['name'], data['user']['phone'],
                        data['user']['otc'])
        pereval.add_coords(data['coords']['latitude'], data['coords']['longitude'], data['coords']['height'])

        img_id_1 = pereval.get_img_id(data['images'][0]['title'])
        try:
            img_id_2 = pereval.get_img_id(data['images'][1]['title'])
        except:
            pass

        try:
            img_id_3 = pereval.get_img_id(data['images'][2]['title'])
        except:
            pass

        pereval.add_pereval_images(img_id_1, img_id_2 if img_id_2 else None, img_id_3 if img_id_3 else None)
        pereval.add_level(data['level']['winter'], data['level']['summer'],
                          data['level']['autumn'], data['level']['spring'])

        user_id = pereval.get_user_id(data['user']['email'])
        coords_id = pereval.get_coords_id(data['coords']['latitude'], data['coords']['longitude'],
                                          data['coords']['height'])
        images_id = pereval.get_images_id(img_id_1)
        level_id = pereval.get_level_id(data['level']['winter'], data['level']['summer'],
                                        data['level']['autumn'], data['level']['spring'])

        pereval.add_pereval(date_added=datetime.datetime.utcnow(), user_id=user_id, coords_id=coords_id,
                            beautyTitle=data['beauty_title'], title=data['title'], other_titles=data['other_titles'],
                            connect=data['connect'], add_time=data['add_time'], images_id=images_id,
                            level_id=level_id)
    except OperationalError:
        response = {'status': 500, 'message': 'Ошибка подключения к БД', 'id': None}
    except TypeError:
        response = {'status': 400, 'message': 'Пропущены обязательные поля', 'id': None}
    else:
        pereval_id = pereval.get_pereval_id(images_id)
        response = {'status': 200, 'message': None, 'id': pereval_id}
    finally:
        return json.dumps(response)


@app.route('/submitData/<int:id>/', methods=['GET'])
def get_pereval(id):
    pereval = Pereval()
    data = json.dumps(pereval.get_pereval_by_id(id))
    return data


@app.route('/submitData/<int:id>/', methods=['PATCH'])
def changeData(id, json_data):
    pereval = Pereval()
    if pereval.is_status_new(id):
        try:
            data = json.loads(json_data)
            coords_id = pereval.get_coords_id(data['coords']['latitude'],
                                              data['coords']['longitude'], data['coords']['height'])
            pereval.change_coords(coords_id, data['coords']['latitude'],
                                              data['coords']['longitude'], data['coords']['height'])
            level_id = pereval.get_level_id(data['level']['winter'], data['level']['summer'],
                              data['level']['autumn'], data['level']['spring'])
            pereval.change_level(level_id, data['level']['winter'], data['level']['summer'],
                              data['level']['autumn'], data['level']['spring'])
            if data['images']:
                img_id_1 = pereval.get_img_id(data['images'][0]['title'])
                try:
                    img_id_2 = pereval.get_img_id(data['images'][1]['title'])
                except:
                    pass

                try:
                    img_id_3 = pereval.get_img_id(data['images'][2]['title'])
                except:
                    pass
                images_id = pereval.get_images_id(img_id_1)
                pereval.change_images(images_id, data['images'][0]['title'], data['images'][0]['data'],
                                      data['images'][1]['title'] if img_id_2 else None,
                                      data['images'][1]['data'] if img_id_2 else None,
                                      data['images'][2]['title'] if img_id_3 else None,
                                      data['images'][2]['data'] if img_id_3 else None)

            pereval.change_pereval(id=id, date_added=pereval.get_date_added(id), beautyTitle=data['beauty_title'],
                                   title=data['title'], other_titles=data['other_titles'], connect=data['connect'],
                                   coords_id=coords_id, level_id=level_id, images_id=images_id)
        except TypeError:
            response = {'state': 0, 'message': 'Неверно введённые данные'}
        except OperationalError:
            response = {'state': 0, 'message': 'Ошибка подключения к БД'}
        else:
            response = {'state': 1, 'message': ''}
        return json.dumps(response)

@app.route('/submitData/?user_email=<str:user_email>', methods=['GET'])
def get_users_perevals(user_email):
    pereval = Pereval()
    data = json.dumps(pereval.get_users_perevals(user_email))
    return data


# if __name__ == '__main__':
#     app.debug = True
#     app.run(port=4996)
