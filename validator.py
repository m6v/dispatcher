import functools
import json
import jsonschema
import logging
import sys

from typing import Callable
from lxml import etree


class MessageValidationError(Exception):
    pass


def validator(schema: str) -> Callable:
    '''Валидатор сообщений из двух замыканий json_validate и xml_validate
       schema: имя файла с XML- или JSON-схемой сообщения
    '''

    def json_validate(data: str) -> bool:
        try:
            jschema(instance=json.loads(data.decode()))
            logging.debug("Validation is successful")
            return True
        except json.decoder.JSONDecodeError as err:
            logging.info(f"Data format error: {err}")
        except jsonschema.exceptions.ValidationError as err:
            logging.info(f"Data validation error: {err.message}")
            raise MessageValidationError(err.message)
        return False

    def xml_validate(data: str) -> bool:
        try:
            xmlschema.assertValid(etree.fromstring(data))
            logging.debug("Validation is successful")
            return True
        except etree.DocumentInvalid as err:
            for error in xmlschema.error_log:
                logging.warning("%s in line %d" % (error.message.rstrip("."), error.line))
            raise MessageValidationError(err)
        except etree.XMLSyntaxError as err:
            logging.warning(err)
        return False

    if not schema:
        # Используется в целях отладки, когда схема не задается, и все сообщения считаются валидными
        # В продакшене отключить дефолтное значение fallback="" у параметра конфигурации "schema"
        logging.warning("Schema not defined")
        validate = lambda data: True
        return validate

    logging.debug(f"Try loading {schema} schema...")
    try:
        # Попытка загрузки XML-схемы...
        xmlschema = etree.XMLSchema(etree.parse(schema))
        return xml_validate
    except (FileNotFoundError, OSError) as err:
        logging.error(err)
        sys.exit(1)
    except etree.XMLSyntaxError as err:
        # Игнорируем исключение, чтобы попробовать загрузить JSON-схему
        logging.debug(err)
    try:
        # Попытка загрузки JSON-схемы...
        with open(schema) as file:
            jschema = functools.partial(jsonschema.validate, schema=json.load(file))
            return json_validate
    except json.decoder.JSONDecodeError as err:
        # Ни XML-, ни JSON-схема не загрузились
        logging.debug(err)
        logging.error(f"Unknown schema {schema}")
        sys.exit(1)
