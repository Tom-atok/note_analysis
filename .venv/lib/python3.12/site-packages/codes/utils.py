from types import new_class


def create_cls_instance(d: dict):
    """Create class instances with dict to easily access data."""
    cls = new_class('TurnDict')
    instance = cls()
    for k, v in d.items():
        setattr(instance, k, v)
    return instance
