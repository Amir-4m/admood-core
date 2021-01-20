from admin_auto_filters.filters import AutocompleteFilter


class CostModelPriceFilter(AutocompleteFilter):
    title = 'Cost model price'
    field_name = 'cost_models'


class CategoriesFilter(AutocompleteFilter):
    title = 'Categories'
    field_name = 'categories'
