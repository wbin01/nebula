from django.contrib import admin
from .models import (
    Category, Language, NavItem, NavItemString, Post, PageSetting, PageStyle)


@admin.register(PageStyle)
class PPageStyleAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    pass

@admin.register(NavItemString)
class NavItemStringAdmin(admin.ModelAdmin):
    pass

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass

@admin.register(PageSetting)
class PageSettingAdmin(admin.ModelAdmin):
    pass
