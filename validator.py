import functools
import json
import jsonschema
import logging
import sys

from lxml import etree


def validator(schema: str):

    def json_validate(data: str) -> bool:
        try:
            jschema(instance=json.loads(data.decode()))
            logging.debug("Validation is successful")
            return True
        except json.decoder.JSONDecodeError as err:
            logging.info(f"Data format error: {err}")
        except jsonschema.exceptions.ValidationError as err:
            logging.info(f"Data validation error: {err.message}")
        return False

    def xml_validate(data: str) -> bool:
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

    if not schema:
        logging.warning("Schema not defined")
        # Если схема не задана возвращать True,
        # т.е. валидация сообщений не выполняется
        validate = lambda x: True
        return validate

    try:
        logging.debug(f"Try loading {schema} schema...")
        # Пробуем загрузить XML-схему
        xmlschema = etree.XMLSchema(etree.parse(schema))
        return xml_validate
    except (FileNotFoundError, OSError) as err:
        logging.error(err)
        sys.exit(1)
    except etree.XMLSyntaxError as err:
        # XML-схема не загрузилась, пробуем загрузить JSON-схему
        logging.debug(err)
        try:
            with open(schema) as file:
                jschema = functools.partial(jsonschema.validate, schema=json.load(file))
                return json_validate
        except json.decoder.JSONDecodeError as err:
            logging.debug(err)
            logging.error(f"Unknown schema {schema}")
            sys.exit(1)
