from django.urls import path
from . import views

urlpatterns = [
    path('', views.animaux_list, name='animaux_list'),
    path('animal/<str:id_character>/', views.animal_detail, name='animal_detail'),
    path('animal/<str:id_character>/?<str:message>', views.animal_detail, name='animal_detail_mes'),
    path('equipement/<str:id_equip>/', views.equipement_detail, name='equipement_detail'),
    path('equipement/<str:id_equip>/?<str:message>', views.equipement_detail, name='equipement_detail_mes'),
]