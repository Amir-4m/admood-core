from admin_auto_filters.filters import AutocompleteFilter


class UserFilter(AutocompleteFilter):
    title = 'User'
    field_name = 'user'


class OwnerFilter(AutocompleteFilter):
    title = 'Owner'
    field_name = 'owner'
