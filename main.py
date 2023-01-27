import datetime
import os

from sqlalchemy import create_engine, text, select
from sqlalchemy.schema import Table, MetaData


class Pereval:
    def __init__(self):
        self.engine = create_engine(f'postgresql+psycopg2://{os.getenv("FSTR_DB_LOGIN")}:'
                                    f'{os.getenv("FSTR_DB_PASS")}@{os.getenv("FSTR_DB_HOST")}/Pereval')\
            .execution_options(autocommit=True)
        self.meta = MetaData(self.engine)
        self.coords = Table('coords', self.meta, schema='public', autoload_with=self.engine)
        self.images = Table('image', self.meta, schema='public', autoload_with=self.engine)
        self.levels = Table('level', self.meta, schema='public', autoload_with=self.engine)
        self.pereval_added = Table('pereval_added', self.meta, schema='public', autoload_with=self.engine)
        self.pereval_areas = Table('pereval_areas', self.meta, schema='public', autoload_with=self.engine)
        self.pereval_images = Table('pereval_images', self.meta, schema='public', autoload_with=self.engine)
        self.spr_activities_types = Table('spr_activities_types', self.meta, schema='public', autoload_with=self.engine)
        self.users = Table('user', self.meta, schema='public', autoload_with=self.engine)

    def get_user(self):
        conn = self.engine.connect()
        users = self.users.select()
        return conn.execute(users)

    def add_coords(self, latitude, longitude, height):
        conn = self.engine.connect()
        ins_coords_query = self.coords.insert().values([(text('DEFAULT'), latitude, longitude, height)])
        conn.execute(ins_coords_query)
        conn.commit()

    def add_image(self, title, image):
        conn = self.engine.connect()
        ins_image_query = self.images.insert().values([(text('DEFAULT'), title, image)])
        conn.execute(ins_image_query)
        conn.commit()

    def add_level(self, winter=None, summer=None, autumn=None, spring=None):
        conn = self.engine.connect()
        ins_level_query = self.levels.insert().values([(text('DEFAULT'), winter, summer, autumn, spring)])
        conn.execute(ins_level_query)
        conn.commit()

    def add_pereval(self, date_added, user_id, coords_id, level_id, beautyTitle,
                    title, other_titles, connect, add_time, images_id=None):
        conn = self.engine.connect()
        ins_pereval_query = self.pereval_added.insert().values([(text('DEFAULT'), date_added, images_id, text('DEFAULT'),
                                                                 user_id, coords_id, level_id, beautyTitle, title,
                                                                 other_titles, connect, add_time)])
        conn.execute(ins_pereval_query)
        conn.commit()

    def add_pereval_area(self, title, id_parent=None):
        conn = self.engine.connect()
        ins_pereval_area_query = self.pereval_areas.insert().values([(text('DEFAULT'), id_parent, title)])
        conn.execute(ins_pereval_area_query)
        conn.commit()

    def add_pereval_images(self, date_added, image_id_1, image_id_2=None, image_id_3=None):
        conn = self.engine.connect()
        ins_pereval_images_query = self.pereval_images.insert().values([(text('DEFAULT'), date_added, image_id_1,
                                                                       image_id_2, image_id_3)])
        conn.execute(ins_pereval_images_query)
        conn.commit()

    def add_spr_activities_type(self, title):
        conn = self.engine.connect()
        ins_spr_activities_type_query = self.spr_activities_types.insert().values([(text('DEFAULT'), title)])
        conn.execute(ins_spr_activities_type_query)
        conn.commit()

    def add_user(self, email, fam, name, otc=None):
        conn = self.engine.connect()
        ins_user_query = self.users.insert().values({'id': text('DEFAULT'), 'email': email, 'fam': fam, 'name': name, 'otc': otc})
        conn.execute(ins_user_query)
        conn.commit()


pereval = Pereval()
