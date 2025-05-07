from django.db import models

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
    def __str__(self):
     return f"{self.nom}  - {self.capacite}"
    
class Reservation(models.Model):
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    coordonateur = models.ForeignKey(Coordonateur, on_delete=models.CASCADE)
    def __str__(self):
     return f"{self.filiere}  - {self.classe} - {self.salle} - {self.date} - {self.heure_debut} - {self.heure_fin} - {self.coordonateur}"