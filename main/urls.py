from django.urls import path
from . import views

urlpatterns = [
    path('', views.CaseListView.as_view(), name='index'),
    path('event/toggle/<int:pk>/', views.toggle_event_status, name='toggle_event'),
    path('case/add/', views.create_case_modal, name='add_case'),
    
    # Секция Клиенты
    path('clients/', views.client_list, name='client_list'),
    path('clients/add/', views.client_modal, name='client_add'),
    path('clients/edit/<int:pk>/', views.client_modal, name='client_edit'),
    
    # Секция Все Дела
    path('cases/', views.case_all_list, name='case_all_list'),
    path('cases/add/', views.case_modal, name='case_full_add'),
    path('cases/edit/<int:pk>/', views.case_modal, name='case_full_edit'),
]