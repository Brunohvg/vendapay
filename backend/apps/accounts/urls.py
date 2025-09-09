from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [

    path('', views.CustomLoginView.as_view(), name='login' ),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('equipe/', views.EquipeView.as_view(), name='equipe'),
    #path('lista_equipe/', views.ListTeamMembersView.as_view())
  
  
]