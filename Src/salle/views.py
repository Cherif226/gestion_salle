from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import Coordonateur
from .models import UFR
from .models import Salle, Reservation, Filiere, Classe

# Create your views here.
def login (request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            
            coordonateur = Coordonateur.objects.get(email=email)
            if check_password(password, coordonateur.password):
                # Connexion réussie (tu peux utiliser les sessions ici)
                request.session['coordonateur_id'] = coordonateur.id
                messages.success(request, "Connexion réussie !")
                return redirect('dashboard')  # page après connexion
            else:
                messages.error(request, "Mot de passe incorrect.")
        except Coordonateur.DoesNotExist:
            messages.error(request, "Email introuvable.")

    return render(request, 'index.html')
    

def inscription(request):
    ufrs = UFR.objects.all()  # Pour le champ select

    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        ufr_id = request.POST.get('ufr')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Vérifier si l'UFR est sélectionnée
        if not ufr_id:
            messages.error(request, "Veuillez sélectionner une UFR.")
        elif password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        elif Coordonateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            try:
                ufr_instance = UFR.objects.get(id=ufr_id)
                coordonateur = Coordonateur(
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    ufr=ufr_instance,
                    password=make_password(password)
                )
                coordonateur.save()
                messages.success(request, "Inscription réussie !")
                return redirect('login')
            except UFR.DoesNotExist:
                messages.error(request, "L'UFR sélectionnée n'existe pas.")

    return render(request, 'inscription.html', {'ufrs': ufrs})


def dashboard(request):
    coord_id = request.session.get('coordonateur_id')
    if coord_id:
        coordonateur = Coordonateur.objects.get(id=coord_id)
        
        # Récupérer les filières liées à son UFR
        filieres = Filiere.objects.filter(ufr=coordonateur.ufr).prefetch_related('classe_set')

        # On prépare les données sous forme d'une liste avec les classes
        filieres_et_classes = []
        for filiere in filieres:
            classes = filiere.classe_set.all()
            filieres_et_classes.append({
                'filiere': filiere,
                'classes': classes
            })

        return render(request, 'dashboard.html', {
            'coordonateur': coordonateur,
            'filieres_et_classes': filieres_et_classes
        })
    else:
        return redirect('login')

def reserver_salle(request, filiere_id, classe_id):
    coord_id = request.session.get('coordonateur_id')
    if not coord_id:
        return redirect('login')

    coordonateur = Coordonateur.objects.get(id=coord_id)
    filiere = Filiere.objects.get(id=filiere_id)
    classe = Classe.objects.get(id=classe_id)
    salles = Salle.objects.all()

      # On récupère toutes les réservations pour affichage
    reservations = Reservation.objects.filter(date__gte=timezone.now().date()).order_by('date', 'heure_debut')

    if request.method == 'POST':
        salle_id = request.POST['salle']
        date = request.POST['date']
        debut = request.POST['heure_debut']
        fin = request.POST['heure_fin']

        conflits = Reservation.objects.filter(
            salle_id=salle_id,
            date=date
        ).filter(
            Q(heure_debut__lt=fin) & Q(heure_fin__gt=debut)
        )

        if conflits.exists():
            messages.error(request, "Cette salle est déjà réservée pour cette plage horaire.")
        else:
            Reservation.objects.create(
                filiere=filiere,
                classe=classe,
                salle_id=salle_id,
                date=date,
                heure_debut=debut,
                heure_fin=fin,
                coordonateur=coordonateur
            )
            messages.success(request, "Salle réservée avec succès !")
            return redirect('dashboard')

    return render(request, 'reserver.html', {
        'filiere': filiere,
        'classe': classe,
        'salles': salles,
        'reservations': reservations,
    })