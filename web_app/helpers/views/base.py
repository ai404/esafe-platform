
def getter(object_, attributes):
    """Reads object attributes

    Args:
        object_ (object): Target object.
        attributes (list): List of attributes to extract.

    Yields:
        object: Extracted attribute's value.
    """
    for attribute in attributes:
        if isinstance(attribute, str):
            yield getattr(object_, attribute)
        elif callable(attribute):
            yield attribute(object_)
        else:
            raise TypeError("Unsupported type of attribute!")
