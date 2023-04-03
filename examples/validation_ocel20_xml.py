import pkgutil


def execute_script():
    import lxml.etree

    if not pkgutil.find_loader("lxml"):
        raise Exception("please install lxml in order to validate an XMLOCEL file.")

    xml_file = lxml.etree.parse("../tests/input_data/ocel/ocel20_example.xmlocel")
    xml_validator = lxml.etree.XMLSchema(file="../tests/input_data/ocel/ocel2-validation.xsd")
    is_valid = xml_validator.validate(xml_file)
    print(is_valid)


if __name__ == "__main__":
    execute_script()
