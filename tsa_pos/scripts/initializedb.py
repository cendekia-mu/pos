import os
import sys
from pyramid.paster import setup_logging
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config
from ziggurat_foundations.models.services.user import UserService
from sqlalchemy import Table, select
from ..models import DBSession, Base, User, Group, init_model
from getpass import getpass
import transaction
import csv
def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)



def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    # LogDBSession.configure(bind=engine)
    # Base.metadata.create_all(bind=engine)
    # alembic_run(config_uri, "alembic_base")
    # base_alembic_run(config_uri)

    # reset_sequences()
    Base.metadata.bind = engine
    with transaction.manager:
        init_model()
        user = DBSession.query(User).first()
        if not user:
            user = User()
            user.user_name = 'admin'
            user.email = 'admin'
            UserService.set_password(user, 'admin')
            DBSession.add(user)
            DBSession.flush()   
        group = Group.query().first()
        if not group:
            group = Group()
            group.group_name = 'admin'
            DBSession.add(group)
            DBSession.flush()
            if group not in user.groups: 
                user.groups.append(group)
            DBSession.flush()

        transaction.commit()


def get_file(filename):
    base_dir = os.path.split(__file__)[0]
    fullpath = os.path.join(base_dir, 'data', filename)
    return open(fullpath)


def restore_csv(table, filename, get_file_func=get_file, db_session=DBSession):
    eng = db_session.get_bind()
    q = db_session.query(table)
    if q.first():
        return
    with get_file_func(filename) as f:
        reader = csv.DictReader(f)
        filter_ = dict()
        foreigns = dict()
        is_first = True
        fmap = dict()
        for cf in reader:
            if is_first:
                is_first = False
                for fieldname in cf.keys():
                    if not fieldname:
                        continue
                    try:
                        t = fieldname.split('/')
                    except Exception as e:
                        # print(fieldname, cf.keys())
                        raise e

                    fname_orig = t[0]
                    schema = "public"
                    if t[1:]:
                        t_array = t[1].split('.')
                        if len(t_array) == 2:
                            foreign_table = t_array[0]
                            foreign_field = t_array[1]
                        else:
                            schema = t_array[0]
                            foreign_table = t_array[1]
                            foreign_field = t_array[2]

                        # foreign_table, foreign_field = t[1].split('.')
                        foreign_table = Table(foreign_table, Base.metadata,
                                              # autoload=True,
                                              autoload_with=eng,
                                              schema=schema)
                        foreign_field = getattr(foreign_table.c, foreign_field)
                        foreigns[fieldname] = (foreign_table, foreign_field)
                    fmap[fieldname] = fname_orig

            row = table()
            for fieldname in cf:
                if fieldname in foreigns:
                    foreign_table, foreign_field = foreigns[fieldname]
                    value = cf[fieldname]
                    # merubah v1.4 ke v.2
                    # sql = select([foreign_table]).where(foreign_field == value)
                    sql = select(foreign_table).where(foreign_field == value)

                    # merubah v1.4 ke v.2
                    # q = Base.metadata.bind.execute(sql)
                    with eng.connect() as conn:
                        q = conn.execute(sql)
                    ft = q.fetchone()
                    val = ft and ft.id or None
                    fieldname = fmap[fieldname]
                else:
                    val = cf[fieldname]

                if not val:
                    continue

                if fieldname == 'user_password':
                    UserService.set_password(row, val)

                try:
                    setattr(row, fieldname, val)
                except:
                    pass

            db_session.add(row)
            db_session.flush()
    return True



def ask_password(name):
    while True:
        pass1 = getpass('Tulis password untuk {}: '.format(name))
        if not pass1:
            continue
        pass2 = getpass('Ulangi password untuk {}: '.format(name))
        if pass1 == pass2:
            return pass1
        print('Maaf kedua password tidak sama')
