from django_filters import rest_framework as filters

from api.models import Recipe, Tag


class CustomRecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ["author", "tags"]
