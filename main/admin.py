from django.contrib import admin
from .models import Client, Case, CaseEvent

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'phone', 'email')
    list_filter = ('role',)
    search_fields = ('name',)

class CaseEventInline(admin.TabularInline):
    model = CaseEvent
    extra = 1

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'defendant', 'status')
    inlines = [CaseEventInline]