from django.db import models
from django.utils import timezone
# Create your models here.
class UFR(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom
    
class Coordonateur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    ufr = models.ForeignKey(UFR, on_delete=models.CASCADE)

    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.ufr}"

class Filiere(models.Model):
    nom = models.CharField(max_length=50)
    ufr = models.CharField(max_length=100)  # ex: High-Tech
    def __str__(self):
        return f"{self.nom}  - {self.ufr}"
    
class Classe(models.Model):
    nom = models.CharField(max_length=10)  # ex: L1, L2, L3
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    def __str__(self):
     return f"{self.nom}  - {self.filiere}"
    
class Salle(models.Model):
    nom = models.CharField(max_length=50)
    capacite = models.IntegerField()
    etat = models.CharField(max_length=10, choices=[('libre', 'Libre'), ('occupee', 'Occupée')], default='libre')
    def __str__(self):
     return f"{self.nom}  - {self.capacite} - {self.etat}"
    
class Reservation(models.Model):
    coordonnateur = models.ForeignKey('Coordonateur', on_delete=models.PROTECT)
    salle = models.ForeignKey('Salle', on_delete=models.CASCADE)
    filiere = models.ForeignKey('Filiere', on_delete=models.CASCADE)
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE)
    jour = models.CharField(max_length=10)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    est_occupe = models.BooleanField(default=True)
    date_reservation = models.DateTimeField(auto_now_add=True)
    est_annule = models.BooleanField(default=False)
    date_annulation = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.salle.nom} réservée pour {self.filiere.nom} - {self.classe.nom} le {self.date_reservation.strftime('%d/%m/%Y %H:%M')}"
    