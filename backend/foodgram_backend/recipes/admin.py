from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag

from django import forms


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
    list_display = ('name', 'user', 'cooking_time', 'favorite_count')
    search_fields = ('name', 'user__username')

    def favorite_count(self, obj):
        return obj.count_favorite_users()
    favorite_count.short_description = 'Favorites'


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
