"""
URL configuration for gestion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from salle import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login,name='login'),
    path('inscription/', views.inscription,name='inscription'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('reserver_salle/<int:filiere_id>/<int:classe_id>/', views.reserver_salle,name='reserver_salle'),
    path('reservation/<int:filiere_id>/<int:classe_id>/pdf/', views.reservation_pdf, name='reservation_pdf'),
    path('liste-reservations/', views.liste_reservations, name='liste_reservations'),
    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('annuler-reservation/<int:reservation_id>/', views.annuler_reservation, name='annuler_reservation'),
]
