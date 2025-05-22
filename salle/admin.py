from django.contrib import admin
from .models import Coordonateur
from .models import Classe
from .models import Filiere
from .models import UFR
from .models import Salle
from .models import Reservation

# Register your models here.
admin.site.register(Coordonateur)
admin.site.register(Classe)
admin.site.register(Filiere)
admin.site.register(UFR)
admin.site.register(Salle)
admin.site.register(Reservation)