#!/usr/bin/env python3
import functools
import jsonschema
import logging
from lxml import etree

# Для логирования в файл, добавить filename='app.log' иначе лог в консоль
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

msg = """
<person>
  <id>1</id>
  <name>Sergey Maksimov</name>
  <age>22</age>
</person>
"""

def validator(schema: str):
    '''Вернуть функцию валидации xml-схемы, заданной в файле schema'''
    xmlschema = etree.XMLSchema(etree.parse(schema))
    def validate(msg: str) -> bool:
        try:
            xmlschema.assertValid(etree.fromstring(msg))
            logging.debug("Validation is successful")
            return True
        except etree.DocumentInvalid:
            for error in xmlschema.error_log:
                logging.warning("%s in line %d" % (error.message.rstrip("."), error.line))
        except etree.XMLSyntaxError as err:
            logging.warning(err)
        return False
    return validate

def main():
    validate = validator("schema.xml")
    validate(msg)


if __name__ == "__main__":
    main()
