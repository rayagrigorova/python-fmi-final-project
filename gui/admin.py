from django.contrib import admin
from .models import ShoppingItem, ShoppingList


class ShoppingItemAdmin(admin.ModelAdmin):
    model = ShoppingItem
    ordering = ('name', 'quantity')
    search_fields = ('name',)
    list_display = ('name', 'quantity', 'bought')
    fields = ('name', 'quantity', 'bought')

class ShoppingListAdmin(admin.ModelAdmin):
    model = ShoppingList
    ordering = ('name', 'owner')
    search_fields = ('name',)
    list_display = ('name', 'owner')
    fields = ('name', 'owner')


admin.site.register(ShoppingItem, ShoppingItemAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
