#!/usr/bin/env python3
import logging
from lxml import etree

# Для логирования в файл, добавить filename='app.log' иначе лог в консоль
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

schema_path = "schema.xml"
msg = """
<?xml version="1.0" encoding="UTF-8"?>
<person>
  <id>1</id>
  <name>Sergey Maksimov</name>
  <age>52</age>
</person>
"""


class Validator:
    def __init__(self, schema_path: str):
        xmlschema_doc = etree.parse(schema_path)
        self.xmlschema = etree.XMLSchema(xmlschema_doc)

    def validate(self, msg: str) -> bool:
        try:
            xml_doc = etree.fromstring(msg)
            self.xmlschema.assertValid(xml_doc)
            logging.debug("Validation is successful")
            return True
        except etree.DocumentInvalid:
            for error in self.xmlschema.error_log:
                logging.error("%s in line %d" % (error.message.rstrip("."), error.line))
        except etree.XMLSyntaxError as err:
            logging.error(err)
        return False


def main():
    validator = Validator(schema_path)
    validator.validate(msg)


if __name__ == "__main__":
    main()
