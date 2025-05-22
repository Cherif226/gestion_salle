from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime, timedelta
import locale
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils import timezone 
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
def est_occupe(jour, debut, fin, horaires_occupees):
    return (jour, debut, fin) in horaires_occupees

def reserver_salle(request, filiere_id, classe_id):
    # Vérification de l'authentification du coordonnateur
    coord_id = request.session.get('coordonateur_id')
    if not coord_id:
        return redirect('login')
    
    try:
        coordonateur = Coordonateur.objects.get(id=coord_id)
    except Coordonateur.DoesNotExist:
        messages.error(request, "Coordonnateur non trouvé.")
        return redirect('login')
    
    filiere = get_object_or_404(Filiere, id=filiere_id)
    classe = get_object_or_404(Classe, id=classe_id)
    salles = Salle.objects.all()
    jours_affiches = []
    jours_dates = []
    date_debut = request.GET.get('date_debut')

    # Gestion des dates
    if date_debut:
        try:
            lundi = datetime.strptime(date_debut, "%Y-%m-%d").date()
            for i in range(6):  # Du lundi au samedi
                jour_date = lundi + timedelta(days=i)
                jours_dates.append(jour_date)
                nom_jour = jour_date.strftime('%A')  # Exemple : 'lundi'
                formatted = f"{nom_jour.capitalize()} {jour_date.day} {jour_date.strftime('%B')}"
                jours_affiches.append(formatted)
        except ValueError:
            messages.error(request, "Date invalide.")

    creneaux = [('08:00', '10:00'), ('10:00', '12:00'), ('14:00', '18:00')]

    # Récupération des réservations existantes
    if jours_dates:
        reservations = Reservation.objects.filter(classe=classe, jour__in=jours_dates)
    else:
        reservations = Reservation.objects.filter(classe=classe)

    horaires_occupees = {(str(r.jour), str(r.heure_debut), str(r.heure_fin)) for r in reservations}

    # Gestion des choix de session
    if 'dernier_choix' not in request.session:
        request.session['dernier_choix'] = {}
    dernier_choix = request.session['dernier_choix']

    # Traitement du formulaire
    if request.method == 'POST':
        jour = request.POST.get('jour')
        debut = request.POST.get('heure_debut')
        fin = request.POST.get('heure_fin')
        salle_id = request.POST.get('salle_id')
        key = f"{jour}|{debut}|{fin}"

        # Stockage du choix en session
        dernier_choix[key] = salle_id
        request.session['dernier_choix'] = dernier_choix
        request.session.modified = True  # Force la sauvegarde de la session

        # Vérification des conflits
        conflits = Reservation.objects.filter(
            jour=jour,
            salle_id=salle_id,
            heure_debut__lt=fin,
            heure_fin__gt=debut
        )

        if conflits.exists():
            messages.error(request, f"Salle déjà réservée le {jour} de {debut} à {fin}.")
        else:
            # Création de la réservation avec le coordonnateur
            Reservation.objects.create(
                coordonnateur=coordonateur,
                salle_id=salle_id,
                filiere=filiere,
                classe=classe,
                jour=jour,
                heure_debut=debut,
                heure_fin=fin,
                est_occupe=True,
                date_reservation=timezone.now()  # Utilisation correcte de timezone
            )
            messages.success(request, "Réservation réussie.")
            
    return render(request, 'reservation.html', {
        'coordonateur': coordonateur,
        'filiere': filiere,
        'classe': classe,
        'salles': salles,
        'jours': jours_affiches,
        'jours_dates': jours_dates,
        'creneaux': creneaux,
        'date_debut': date_debut,
        'horaires_occupees': horaires_occupees,
        'dernier_choix': dernier_choix,
    })

from .utils import render_to_pdf  # assure-toi d’avoir créé la fonction render_to_pdf comme vu plus haut

def reservation_pdf(request, filiere_id, classe_id):
    filiere = get_object_or_404(Filiere, id=filiere_id)
    classe = get_object_or_404(Classe, id=classe_id)
    creneaux = [('08:00', '10:00'), ('10:00', '12:00'), ('14:00', '18:00')]

    date_debut_str = request.GET.get('date_debut')
    jours = []
    jours_semaine = []  # Pour le matching avec la base

    if date_debut_str:
        try:
            date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
            for i in range(6):
                jour_date = date_debut + timedelta(days=i)
                jours.append(jour_date.strftime('%A %d %B %Y'))  # Format complet
                jours_semaine.append(jour_date.strftime('%A %d %B').lower())  # Format matching
        except ValueError:
            pass

    # Debug: Affiche les jours attendus
    print("Jours de la semaine:", jours_semaine)

    planning = {}
    for res in Reservation.objects.filter(classe=classe):
        # Normalisation du format
        res_jour = res.jour.strip().lower()
        
        if res_jour in jours_semaine:
            idx = jours_semaine.index(res_jour)
            jour_complet = jours[idx]
            
            # Gestion robuste des heures
            heure_debut = res.heure_debut[:5] if isinstance(res.heure_debut, str) else res.heure_debut.strftime('%H:%M')
            heure_fin = res.heure_fin[:5] if isinstance(res.heure_fin, str) else res.heure_fin.strftime('%H:%M')
            
            key = f"{jour_complet}|{heure_debut}|{heure_fin}"
            planning[key] = res.salle.nom

    # Debug: Affiche le planning généré
    print("Planning généré:", planning)

    context = {
        'filiere': filiere,
        'classe': classe,
        'jours': jours,
        'creneaux': creneaux,
        'planning': planning,
    }

    pdf = render_to_pdf('emploi_du_temps.html', context)
    return HttpResponse(pdf, content_type='application/pdf')


def liste_reservations(request):
    # Récupérer toutes les réservations triées par date
    reservations = Reservation.objects.all().order_by('-date_reservation')
    
    context = {
        'reservations': reservations
    }
    return render(request, 'liste.html', context)


def mes_reservations(request):
    coord_id = request.session.get('coordonateur_id')
    if not coord_id:
        return redirect('login')
    
    coordonateur = Coordonateur.objects.get(id=coord_id)
    
    # Récupérer les réservations du coordonnateur, triées par date
    reservations = Reservation.objects.filter(
        coordonnateur=coordonateur
    ).order_by('-date_reservation')
    
    return render(request, 'mes_reservations.html', {
        'coordonateur': coordonateur,
        'reservations': reservations
    })


###Annulation de reservations
def annuler_reservation(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(
            Reservation,
            id=reservation_id,
            coordonnateur_id=request.session.get('coordonateur_id')
        )
        
        # Marquer comme annulé au lieu de supprimer
        reservation.est_annule = True
        reservation.est_occupe = False
        reservation.save()
        
        # Libérer la salle
        salle = reservation.salle
        salle.etat = 'libre'
        salle.save()
        
        messages.success(request, "Réservation annulée avec succès.")
    
    return redirect('mes_reservations')