from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag

from django import forms
# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('name', 'color', 'slug')


# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ('name', 'measurement_unit')
#     search_fields = ('name',)


# @admin.register(Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = (
#         'name', 'user', 'cooking_time', 'favorite_count'
#     )
#     search_fields = ('name', 'user__username')

#     def favorite_count(self, obj):
#         return obj.count_favorite_users()
#     favorite_count.short_description = 'Favorites'
class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1  # Number of empty forms to display


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = []


class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'user', 'cooking_time', 'favorite_count')
    search_fields = ('name', 'user__username')

    def favorite_count(self, obj):
        return obj.count_favorite_users()
    favorite_count.short_description = 'Favorites'


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
