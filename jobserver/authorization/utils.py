import itertools

from .mappers import get_org_roles_for_user, get_project_roles_for_user


def _validate_context(allowed_keys, context):
    """
    Ensure keys and types-of-values in context are correct

    When passing in context to either has_permission or has_role we want to
    help developers track down incorrect keys or incorrect values.

    For example, given this call:

        _validate_context(["project"], {"projects": project})

    we want to tell the developer that "projects" is an invalid key.

    Similarly we want to make sure the contextual objects passed in are valid
    for the keys used, take the following function call:

        _validate_context(["project"], {"project": user})

    We want to tell the developer that a "project" key must map to a Project
    (model) instance.
    """
    if not context:
        return

    # checks based on the allowed list passed in
    unknown_keys = set(context.keys()) - set(allowed_keys)
    if unknown_keys:
        msg = "Some invalid keys were used in the context:"

        for key in unknown_keys:
            msg += f"\n - {key}"

        raise ValueError(msg)

    # import here to avoid circular imports
    from jobserver import models

    type_map = {
        "org": models.Org,
        "project": models.Project,
    }
    incorrect_types = {}
    for key, value in context.items():
        model = type_map[key]
        if not isinstance(value, model):
            incorrect_types[key] = type(value)

    if not incorrect_types:
        return

    msg = "Some invalid values were used in the context:"
    for key, value in incorrect_types.items():
        expected = type_map[key]
        msg += (
            f'\n - key "{key}" got a {value.__name__}, expected a {expected.__name__}'
        )

    raise ValueError(msg)


def _get_roles(user, **context):
    """
    Build up a set of Roles from the User and context

    A User's Roles can come from various locations, and be local or global,
    this function gathers them from those locations using the passed context,
    combining them into the returned set.
    """

    # map mappers to keys
    mappers_lut = {
        "org": get_org_roles_for_user,
        "project": get_project_roles_for_user,
    }

    # validate the context's keys and values
    _validate_context(mappers_lut.keys(), context)

    # build up an initial set of roles based solely on the User
    roles = set(user.roles)

    # update the set with any Roles tied to the objects in the context
    for key, value in context.items():
        mapper = mappers_lut.get(key)
        roles |= set(mapper(value, user))

    return roles


def has_permission(user, permission, **context):
    if not user.is_authenticated:
        return False

    roles = _get_roles(user, **context)

    # Flatten each Roles permissions list into a single iterable
    permissions = itertools.chain.from_iterable(r.permissions for r in roles)

    # convert the itertools.chain generator into a set so we can check membership
    permissions = set(permissions)

    # return a boolean for whether the requested permission is in that set
    return permission in permissions


def has_role(user, role, **context):
    if not user.is_authenticated:
        return False

    return role in _get_roles(user, **context)