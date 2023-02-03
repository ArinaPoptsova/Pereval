import datetime
import json
import os
from sqlalchemy import create_engine, text, select, and_
from sqlalchemy.orm import Session, sessionmaker, aliased
from sqlalchemy.schema import Table, MetaData
from schemas import DataSchema


class Pereval:
    def __init__(self):
        self.engine = create_engine(f'postgresql+psycopg2://{os.getenv("FSTR_DB_LOGIN")}:'
                                    f'{os.getenv("FSTR_DB_PASS")}@{os.getenv("FSTR_DB_HOST")}/Pereval?client_encoding=utf8')\
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
        self.dataschema = DataSchema()

    def get_joined_pereval_query(self):
        img_1 = aliased(self.images)
        img_2 = aliased(self.images)
        img_3 = aliased(self.images)
        return select(self.pereval_added.c.date_added, self.pereval_added.c.status, self.pereval_added.c.beautyTitle,
                               self.pereval_added.c.title.label('pereval_title'), self.pereval_added.c.other_titles,
                               self.pereval_added.c.connect, self.pereval_added.c.add_time, self.users.c.fam,
                               self.users.c.name, self.users.c.otc, self.users.c.email, self.users.c.phone,
                               self.coords.c.latitude, self.coords.c.longitude, self.coords.c.height,
                               self.levels.c.winter, self.levels.c.summer, self.levels.c.spring, self.levels.c.autumn,
                               img_1.c.title.label('img_1_title'), img_1.c.img.label('img_1'),
                               img_2.c.title.label('img_2_title'), img_2.c.img.label('img_2'),
                               img_3.c.title.label('img_3_title'), img_3.c.img.label('img_3'))\
            .join(self.users, self.users.c.id == self.pereval_added.c.user_id)\
            .join(self.coords, self.coords.c.id == self.pereval_added.c.coords_id)\
            .outerjoin(self.levels, self.levels.c.id == self.pereval_added.c.level_id)\
            .outerjoin(self.pereval_images, self.pereval_images.c.id == self.pereval_added.c.images_id)\
            .outerjoin(img_1, img_1.c.id == self.pereval_images.c.img_id_1)\
            .outerjoin(img_2, img_2.c.id == self.pereval_images.c.img_id_2)\
            .outerjoin(img_3, img_3.c.id == self.pereval_images.c.img_id_3)

    def get_pereval_by_id(self, id):
        pereval_query = self.get_joined_pereval_query().where(self.pereval_added.c.id == id)
        result = self.conn.execute(pereval_query).fetchone()
        serialized_data = self.dataschema.dump(result)
        serialized_data = {k: v.decode() if type(v) == bytes else v for k, v in serialized_data.items()}
        return serialized_data

    def get_users_perevals(self, email):
        user_id = self.get_user_id(email)
        pereval_query = self.get_joined_pereval_query().where(self.pereval_added.c.user_id == user_id)
        result = self.conn.execute(pereval_query).fetchall()
        serialized_data = []
        for i in range(len(result)):
            serialized_data_one = self.dataschema.dump(result[i])
            serialized_data_one = {k: v.decode() if type(v) == bytes else v for k, v in serialized_data_one.items()}
            serialized_data.append(serialized_data_one)
        return serialized_data

    def get_user_id(self, email):
        get_id_query = select(self.users.c.id).where(self.users.c.email == email)
        return self.conn.execute(get_id_query).fetchone()[0]

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

    def get_img_id(self, title):
        get_id_query = select(self.images.c.id).where(self.images.c.title == title)
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

    def change_images(self, images_id, img_1_title, img_1_img, img_2_title=None, img_2_img=None,
                         img_3_title=None, img_3_img=None):
        img_id_1 = self.conn.execute(select(self.pereval_images.c.img_id_1)
                                     .where(self.pereval_images.c.id == images_id)).fetchone()[0]
        img_id_2 = self.conn.execute(
            select(self.pereval_images.c.img_id_2).where(self.pereval_images.c.id == images_id)).fetchone()[0]
        img_id_3 = self.conn.execute(
            select(self.pereval_images.c.img_id_3).where(self.pereval_images.c.id == images_id)).fetchone()[0]
        img_data = [{'id': img_id_1, 'title': img_1_title, 'img': img_1_img},
                    {'id': img_id_2, 'title': img_2_title, 'img': img_2_img},
                    {'id': img_id_3, 'title': img_3_title, 'img': img_3_img}]
        for i in range(3):
            if img_data[i]['id']:
                self.change_image(img_data[i]['id'], img_data[i]['title'], img_data[i]['img'])
            else:
                self.add_image(img_data[i]['title'], img_data[i]['img'])
                img_data[i]['id'] = self.get_img_id(img_data[i]['title'])
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
