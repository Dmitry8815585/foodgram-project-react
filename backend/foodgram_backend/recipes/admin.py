from django import forms
from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = []


class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    inlines = [RecipeIngredientInline]
    list_display = (
        'name', 'user', 'cooking_time', 'favorite_count'
    )
    search_fields = ('name', 'user__username', 'tags__name')

    def favorite_count(self, obj):
        return obj.count_favorite_users()
    favorite_count.short_description = 'Favorites'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient,  IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
