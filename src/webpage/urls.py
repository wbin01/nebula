from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.index, name='index'),

    path('<str:lang>/',
         views.index, name='index'),

    path('<str:lang>/post/<str:url>/',
         views.post, name='post'),

    path('<str:lang>/search/<str:text>/',
         views.search, name='search'),

    path('<str:lang>/tag/<str:text>/',
         views.tag, name='tag'),

    path('<str:lang>/settings/<str:text>/',
         views.settings, name='settings'),

    path('<str:lang>/<str:category_name>/',
         views.category, name='category'),

    path('<str:lang>/<str:category_name>/<str:sub_category_name>/',
         views.sub_category, name='sub_category'),

    path('admin/',
         views.admin, name='admin'),
]
