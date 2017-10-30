from peewee import *

db = SqliteDatabase('granjasenl.db')


class Granja(Model):
    id = IntegerField(primary_key=True)
    titulo = CharField()
    fecha = CharField()
    lugar = CharField()
    comentario = CharField()
    id_creador = IntegerField()
    status = IntegerField()

    class Meta:
        database = db
        db_table = "genl_granja"

class Participantes(Model):
    id = IntegerField(primary_key=True)
    granja_id = IntegerField()
    user_id = IntegerField()
    user_name = CharField()
    user_nick = CharField()
    status = CharField()

    class Meta:
        database = db
        db_table = "genl_participantes"
