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

        pereval.add_pereval(datetime.datetime.utcnow(), user_id, coords_id,
                            data['beauty_title'], data['title'], data['other_titles'],
                            data['connect'], data['add_time'], images_id,
                            level_id)
    except OperationalError:
        response = {'status': 500, 'message': 'Ошибка подключения к БД', 'id': None}
    except TypeError:
        response = {'status': 400, 'message': 'Пропущены обязательные поля', 'id': None}
    else:
        pereval_id = pereval.get_pereval_id(images_id)
        response = {'status': 200, 'message': None, 'id': pereval_id}
    finally:
        return json.dumps(response)


if __name__ == '__main__':
    app.debug = True
    app.run(port=4996)
