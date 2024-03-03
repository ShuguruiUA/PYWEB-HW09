import json

from mongoengine.errors import NotUniqueError

from models import Author, Quote

"""
Скрипт за допомогою JSON зчитує файли та за допомогою моделей заповнює базу даних із кодуванням 'utf-8'.
"""

if __name__ == '__main__':
    with open('authors.json', encoding='utf-8') as file:
        data = json.load(file)
        for el in data:
            try:
                author = Author(fullname=el.get('fullname'),
                                born_date=el.get('born_date'),
                                born_location=el.get('born_location'),
                                description=el.get('description')
                                )
                author.save()
            except NotUniqueError:
                print(f"Author with {el.get('fullname')} already exists")

    with open('quotes.json', encoding='utf-8') as file:
        data = json.load(file)
        for el in data:
            try:
                author, *_ = Author.objects(fullname=el.get('author'))
                quote = Quote(tags=el.get('tags'),
                              author=author,
                              quote=el.get('quote')
                              )
                quote.save()
            except NotUniqueError:
                print(f"Quotes {el.get('quote')} already exists")
