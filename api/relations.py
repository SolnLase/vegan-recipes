from django.shortcuts import get_object_or_404
from rest_framework.serializers import HyperlinkedRelatedField
from rest_framework.reverse import reverse
from rest_framework.fields import get_attribute


class CustomMultiLookupHyperlink(HyperlinkedRelatedField):
    """
    HyperLinkedRelated field which accept multiple lookup arguments,
    as a dict which consists of lookup_url_kwarg and lookup_field
    as key and value respectively, or as a tuple in which at the same time
    argument is lookup_url_kwarg and lookup_field. Default are pk
    """

    lookup_kwarg_fields = ('pk',)

    def __init__(self, view_name=None, **kwargs):
        # Dict containing lookup_url_kwarg, lookup_field pairs
        lookup_kwarg_fields = kwargs.pop(
            'lookup_kwarg_fields', self.lookup_kwarg_fields
        )

        # Transform it to dictionary if it's tuple or list type
        if isinstance(lookup_kwarg_fields, dict):
            self.lookup_kwarg_fields = lookup_kwarg_fields
        elif isinstance(lookup_kwarg_fields, (tuple, list)):
            lookup_dict = {}
            for kwarg_field in lookup_kwarg_fields:
                lookup_dict[kwarg_field] = kwarg_field

            self.lookup_kwarg_fields = lookup_dict

        super().__init__(view_name, **kwargs)

    def get_object(self, view_name, view_args, view_kwargs):
        """
        Get the related object based on multiple lookup fields
        """
        lookup_kwarg_fields = self.lookup_kwarg_fields
        # Kwarg arguments for object lookup with get
        lookup_kwargs = {}
        for lookup_url_kwarg, lookup_field in lookup_kwarg_fields.items():
            lookup_value = view_kwargs[lookup_url_kwarg]
            lookup_kwargs[lookup_field] = lookup_value

        queryset = self.get_queryset()
        return get_object_or_404(queryset, **lookup_kwargs)

    def get_attribute(self, instance):
        """
        Return just the related object
        """
        return get_attribute(instance, self.source_attrs)

    def get_url(self, obj, view_name, request, format):
        """
        Get the url of the related based on lookup fields
        """
        lookup_kwarg_fields = self.lookup_kwarg_fields
        url_kwargs = {}

        for lookup_url_kwarg, lookup_field in lookup_kwarg_fields.items():
            # If it has related field(s), seperate them and get value from every of them
            # untill you get the value of the last one
            if '__' in lookup_field:
                relational_fields = lookup_field.split('__')
                related_obj_value = obj
                for relational_field in relational_fields:
                    if related_obj_value is None:
                        break
                    related_obj_value = getattr(related_obj_value, relational_field)
                lookup_value = related_obj_value
            else:
                lookup_value = getattr(obj, lookup_field)
            url_kwargs[lookup_url_kwarg] = lookup_value

        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)
