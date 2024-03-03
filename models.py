from bson import json_util

from mongoengine import connect, Document, StringField, ListField, ReferenceField, CASCADE

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

mongo_user = config.get('DB', 'user')
mongodb_pass = config.get('DB', 'pass')
db_name = config.get('DB', 'db_name')
domain = config.get('DB', 'domain')

connect(host=f"""mongodb+srv://{mongo_user}:{mongodb_pass}@{domain}/{db_name}?retryWrites=true&w=majority""", ssl=True)

# Створюємо моделі для бази за допомогою mongoengine

class Author(Document):
    fullname = StringField(max_length=120, required=True, unique=True)
    born_date = StringField(max_length=30)
    born_location = StringField(max_length=180)
    description = StringField()
    meta = {"collection": "authors"}


class Quote(Document):
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    tags = ListField(StringField(max_length=100))
    quote = StringField(unique=True)
    meta = {"collection": "quotes"}

# для коректного повернення імені автора перевизначаємо метод to_json
    def to_json(self, *args, **kwargs):
        data = self.to_mongo(*args, **kwargs)
        data["author"] = self.author.fullname
        return json_util.dumps(data, ensure_ascii=False)
