import datetime
import os

from sqlalchemy import create_engine, text, select, and_
from sqlalchemy.schema import Table, MetaData


class Pereval:
    def __init__(self):
        self.engine = create_engine(f'postgresql+psycopg2://{os.getenv("FSTR_DB_LOGIN")}:'
                                    f'{os.getenv("FSTR_DB_PASS")}@{os.getenv("FSTR_DB_HOST")}/Pereval')\
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
                    title, other_titles, connect, add_time, images_id=None, level_id=None):
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
