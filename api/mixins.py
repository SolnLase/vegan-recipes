from rest_framework.generics import get_object_or_404


class MultipleFieldLookupMixin:
    """
    Get object based on multiple url kwargs
    """
    def get_object(self):
        queryset = self.get_queryset()
        filter_args = {}
        for field in self.multiple_lookup_fields:
            if self.kwargs.get(field, None):
                filter_args[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter_args)
        self.check_object_permissions(self.request, obj)
        return obj


class MultipleFieldQuerysetMixin:
    """
    Get queryset based on multiple url kwargs
    """
    def get_queryset(self):
        filter_args = {}
        for field in self.queryset_fields:
            if self.kwargs.get(field, None):
                filter_args[field] = self.kwargs[field]
        return self.queryset.filter(**filter_args)
