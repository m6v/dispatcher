import functools
import json
import jsonschema
import logging
import sys
import os

from lxml import etree

def json_validator(schema: str):
    if not schema:
        logging.warning("Schema not defined")
        # Если схема не задана возвращать True, т.е. валидация сообщений не выполняется
        validate = lambda x: True
        return validate
    try:
        with open(schema) as file:
            jschema = functools.partial(jsonschema.validate, schema=json.load(file))
    except (FileNotFoundError, json.decoder.JSONDecodeError) as err:
        logging.error(err)
        sys.exit(1)

    def validate(data: str) -> bool:
        try:
            jschema(instance=json.loads(data.decode()))
            logging.debug("Validation is successful")
            return True
        except json.decoder.JSONDecodeError as err:
            logging.info(f"Data format error: {err}")
        except jsonschema.exceptions.ValidationError as err:
            logging.info(f"Data validation error: {err.message}")
        return False
    return validate

def xml_validator(schema: str):
    '''Вернуть функцию валидации xml-схемы, заданной в файле schema'''
    try:
        xmlschema = etree.XMLSchema(etree.parse(schema))
    except etree.XMLSyntaxError as err:
        logging.error(err)
        sys.exit(1)

    def validate(data: str) -> bool:
        try:
            xmlschema.assertValid(etree.fromstring(data))
            logging.debug("Validation is successful")
            return True
        except etree.DocumentInvalid:
            for error in xmlschema.error_log:
                logging.warning("%s in line %d" % (error.message.rstrip("."), error.line))
        except etree.XMLSyntaxError as err:
            logging.warning(err)
        return False
    return validate
