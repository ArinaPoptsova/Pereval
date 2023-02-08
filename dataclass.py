import datetime
import json
import os
from sqlalchemy import create_engine, text, select, and_
from sqlalchemy.orm import Session, sessionmaker, aliased
from sqlalchemy.schema import Table, MetaData
from schemas import DataSchema, UserSchema, CoordsSchema, LevelSchema, ImageSchema, validate_email


class Pereval:
    def __init__(self):
        self.engine = create_engine(f'postgresql+psycopg2://{os.getenv("FSTR_DB_LOGIN")}:{os.getenv("FSTR_DB_PASS")}'
                                    f'@{os.getenv("FSTR_DB_HOST")}/Pereval')\
            .execution_options(autocommit=True)
        self.meta = MetaData(self.engine)
        self.conn = self.engine.connect()
        self.coords = Table('coords', self.meta, schema='public', autoload_with=self.engine)
        self.images = Table('image', self.meta, schema='public', autoload_with=self.engine)
        self.levels = Table('level', self.meta, schema='public', autoload_with=self.engine)
        self.pereval_added = Table('pereval_added', self.meta, schema='public', autoload_with=self.engine)
        self.pereval_areas = Table('pereval_areas', self.meta, schema='public', autoload_with=self.engine)
        self.pereval_images = Table('pereval_images', self.meta, schema='public', autoload_with=self.engine)
        self.spr_activities_types = Table('spr_activities_types', self.meta, schema='public', autoload_with=self.engine)
        self.users = Table('user', self.meta, schema='public', autoload_with=self.engine)

    def get_pereval_by_id(self, id):
        pereval_query = select(self.pereval_added).where(self.pereval_added.c.id == id)
        pereval_data = self.conn.execute(pereval_query).fetchone()
        user_data = self.conn.execute(select(self.users).where(self.users.c.id == pereval_data.user_id)).fetchone()
        coords_data = self.conn.execute(select(self.coords)
                                        .where(self.coords.c.id == pereval_data.coords_id)).fetchone()
        level_data = self.conn.execute(select(self.levels).where(self.levels.c.id == pereval_data.level_id)).fetchone()
        pereval_images_data = self.conn.execute(select(self.pereval_images)
                                                .where(self.pereval_images.c.id == pereval_data.images_id)).fetchone()
        img_1 = self.conn.execute(select(self.images).where(self.images.c.id == pereval_images_data.img_id_1)).fetchone()
        img_2 = self.conn.execute(select(self.images).where(self.images.c.id == pereval_images_data.img_id_2)).fetchone()
        img_3 = self.conn.execute(select(self.images).where(self.images.c.id == pereval_images_data.img_id_3)).fetchone()
        img_list = [img_1, img_2, img_3]
        serialized_pereval_data = DataSchema().dump(pereval_data)
        serialized_user_data = UserSchema().dump(user_data)
        serialized_coords_data = CoordsSchema().dump(coords_data)
        serialized_level_data = LevelSchema().dump(level_data)
        serialized_images_data = []
        for i in range(len(img_list)):
            if img_list[i]:
                serialized_images_data.append(ImageSchema().dump(img_list[i]))
                serialized_images_data[i]['data'] = serialized_images_data[i]['data'].decode()
        serialized_data = {**serialized_pereval_data, 'user': serialized_user_data,
                           'coords': serialized_coords_data, 'level': serialized_level_data,
                           'images': serialized_images_data}
        return serialized_data

    def get_users_perevals(self, email):
        user_id = self.get_user_id(email)
        pereval_query = select(self.pereval_added).where(self.pereval_added.c.user_id == user_id)
        pereval_data = self.conn.execute(pereval_query).fetchall()
        serialized_data = []
        for i in range(len(pereval_data)):
            pereval_data_one = self.get_pereval_by_id(pereval_data[i].id)
            serialized_data.append(pereval_data_one)
        return serialized_data

    def get_user_id(self, email):
        get_id_query = select(self.users.c.id).where(self.users.c.email == email)
        return self.conn.execute(get_id_query).fetchone()[0]

    def is_user_exist(self, email):
        get_user_query = select(self.users).where(self.users.c.email == email)
        user = self.conn.execute(get_user_query).fetchone()
        if user:
            return True
        else:
            return False

    def get_image(self, title):
        get_image_query = select(self.images).where(self.images.c.title == title)
        return self.conn.execute(get_image_query).fetchone()

    def get_coords_id(self, latitude, longitude, height):
        get_id_query = select(self.coords.c.id).where(and_(self.coords.c.latitude == latitude,
                                                            self.coords.c.longitude == longitude,
                                                            self.coords.c.height == height))
        return self.conn.execute(get_id_query).fetchone()[0]

    def get_images_id(self, image_id):
        get_id_query = select(self.pereval_images.c.id).where(self.pereval_images.c.img_id_1 == image_id)
        return self.conn.execute(get_id_query).fetchone()[0]

    def get_level_id(self, winter=None, summer=None, autumn=None, spring=None):
        get_id_query = select(self.levels.c.id).where(and_(self.levels.c.winter == winter,
                                                           self.levels.c.summer == summer,
                                                           self.levels.c.autumn == autumn,
                                                           self.levels.c.spring == spring))
        return self.conn.execute(get_id_query).fetchone()[0]

    def get_pereval_id(self, images_id):
        get_id_query = select(self.pereval_added.c.id).where(self.pereval_added.c.images_id == images_id)
        return self.conn.execute(get_id_query).fetchone()[0]

    def get_date_added(self, id):
        get_date_query = select(self.pereval_added.c.date_added).where(self.pereval_added.c.id == id)
        return self.conn.execute(get_date_query).fetchone()[0]

    def is_status_new(self, id):
        get_status_query = select(self.pereval_added.c.status).where(self.pereval_added.c.id == id)
        status = self.conn.execute(get_status_query).fetchone()[0]
        if status == 'new':
            return True
        else:
            return False

    def add_coords(self, latitude, longitude, height):
        ins_coords_query = self.coords.insert().values([(text('DEFAULT'), latitude, longitude, height)])
        self.conn.execute(ins_coords_query)
        self.conn.commit()

    def add_image(self, title, image):
        ins_image_query = self.images.insert().values([(text('DEFAULT'), title, image)])
        self.conn.execute(ins_image_query)
        self.conn.commit()

    def add_level(self, winter=None, summer=None, autumn=None, spring=None):
        ins_level_query = self.levels.insert().values([(text('DEFAULT'), winter, summer, autumn, spring)])
        self.conn.execute(ins_level_query)
        self.conn.commit()

    def add_pereval(self, date_added, user_id, coords_id, beautyTitle,
                    title, other_titles, add_time, connect=None, images_id=None, level_id=None):
        ins_pereval_query = self.pereval_added.insert().values([(text('DEFAULT'), date_added, images_id, text('DEFAULT'),
                                                                 user_id, coords_id, level_id, beautyTitle, title,
                                                                 other_titles, connect, add_time)])
        self.conn.execute(ins_pereval_query)
        self.conn.commit()

    def add_pereval_area(self, title, id_parent=None):
        ins_pereval_area_query = self.pereval_areas.insert().values([(text('DEFAULT'), id_parent, title)])
        self.conn.execute(ins_pereval_area_query)
        self.conn.commit()

    def add_pereval_images(self, image_id_1, image_id_2=None, image_id_3=None):
        ins_pereval_images_query = self.pereval_images.insert().values([(text('DEFAULT'), image_id_1,
                                                                       image_id_2, image_id_3)])
        self.conn.execute(ins_pereval_images_query)
        self.conn.commit()

    def add_spr_activities_type(self, title):
        ins_spr_activities_type_query = self.spr_activities_types.insert().values([(text('DEFAULT'), title)])
        self.conn.execute(ins_spr_activities_type_query)
        self.conn.commit()

    def add_user(self, email, fam, name, phone, otc=None):
        ins_user_query = self.users.insert().values((text('DEFAULT'), email, fam, name, otc, phone))
        self.conn.execute(ins_user_query)
        self.conn.commit()

    def change_pereval(self, id, date_added, beautyTitle, title, other_titles,
                       connect, coords_id, level_id=None, images_id=None):
        up_pereval_query = self.pereval_added.update().where(self.pereval_added.c.id == id).values(
            {'date_added': date_added, 'beautyTitle': beautyTitle, 'title': title, 'other_titles': other_titles,
             'connect': connect, 'coords_id': coords_id, 'level_id': level_id, 'images_id': images_id}
        )
        self.conn.execute(up_pereval_query)
        self.conn.commit()

    def change_coords(self, coords_id, latitude, longitude, height):
        up_coords_query = self.coords.update().where(self.coords.c.id == coords_id).values(
            {'latitude': latitude, 'longitude': longitude, 'height': height}
        )
        self.conn.execute(up_coords_query)
        self.conn.commit()

    def change_level(self, level_id, winter=None, summer=None, autumn=None, spring=None):
        up_level_query = self.levels.update().where(self.levels.c.id == level_id).values(
            {'winter': winter, 'summer': summer, 'autumn': autumn, 'spring': spring}
        )
        self.conn.execute(up_level_query)
        self.conn.commit()

    def change_images(self, images_id, img_1_id, img_1_title, img_1_img, img_2_id=None, img_2_title=None, img_2_img=None,
                         img_3_id=None, img_3_title=None, img_3_img=None):
        img_data = [{'id': img_1_id, 'title': img_1_title, 'img': img_1_img},
                    {'id': img_2_id, 'title': img_2_title, 'img': img_2_img},
                    {'id': img_3_id, 'title': img_3_title, 'img': img_3_img}]
        for i in range(3):
            if img_data[i]['id']:
                self.change_image(img_data[i]['id'], img_data[i]['title'], img_data[i]['img'])
            else:
                self.add_image(img_data[i]['title'], img_data[i]['img'])
                img_data[i]['id'] = self.get_image(img_data[i]['title']).id
        up_images_id_query = self.pereval_images.update().where(self.pereval_images.c.id == images_id).values(
            {'img_id_1': img_data[0]['id'], 'img_id_2': img_data[1]['id'], 'img_id_3': img_data[2]['id']}
        )
        self.conn.execute(up_images_id_query)
        self.conn.commit()

    def change_image(self, img_id, title, image):
        up_image_query = self.images.update().where(self.images.c.id == img_id).values(
            {'title': title, 'img': image}
        )
        self.conn.execute(up_image_query)
        self.conn.commit()


pereval = Pereval()
# pereval.add_image('0img', bytes(10))
# print(pereval.get_image('0img').title)
# print(pereval.get_user_id('arina.poptsova@yamdex.ru'))
print(pereval.get_pereval_by_id(39))
