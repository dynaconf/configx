from lib.shared.types import CompoundTypes


def normalize_compound_type(compound: CompoundTypes):
    """
    Transform list to a dict-form by setting index as keys.
    Bypasses if already dict

    Eg. `['foo', 'bar'] -> {1:'foo', 2:'bar'}`
    """
    if isinstance(compound, list):
        new_form = {}
        for i, e in enumerate(compound):
            new_form[i] = e
        return new_form
    return compound
