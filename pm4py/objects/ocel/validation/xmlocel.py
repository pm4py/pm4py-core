import pkgutil


def apply(input_path, validation_path, parameters=None):
    import lxml.etree

    if not pkgutil.find_loader("lxml"):
        raise Exception("please install lxml in order to validate an XMLOCEL file.")

    if parameters is None:
        parameters = {}

    xml_file = lxml.etree.parse(input_path)
    xml_validator = lxml.etree.XMLSchema(file=validation_path)
    is_valid = xml_validator.validate(xml_file)
    return is_valid
