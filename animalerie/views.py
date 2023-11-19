from django.shortcuts import render, get_object_or_404, redirect
from .forms import ChangeLieuForm, ChangeCapaciteForm
from .models import Equipement, Character

# Create your views here.
def animaux_list(request):
    animaux = Character.objects.all().order_by('id_character')
    equipements = Equipement.objects.all().order_by('id_equip')
    return render(request, 'animalerie/animaux_list.html', {'animaux': animaux, 'equipements': equipements})

def check_changement(etat,nouveau_lieu):
    if etat == "Affamé" and nouveau_lieu == "Mangeoire":
        return True
    elif etat == "Repus" and nouveau_lieu == "Roue":
        return True
    elif etat == "Fatigué" and nouveau_lieu == "Nid":
        return True
    elif etat == "Endormi" and nouveau_lieu == "Litière":
        return True
    else:
        return False
    
def changement_etat(lieu):
    if lieu == 'Litière':
        etat = "Affamé"
    elif lieu == 'Roue':
        etat = "Fatigué"
    elif lieu == 'Mangeoire':
        etat = "Repus"
    elif lieu == 'Nid':
        etat = "Endormi"
    return etat


def animal_detail(request, id_character):
    animal = get_object_or_404(Character, id_character=id_character)
    ancien_lieu = get_object_or_404(Equipement, id_equip=animal.lieu.id_equip)

    form = ChangeLieuForm(request.POST, instance=animal)

    error = None
    message = ""
    if request.method == "POST"and form.is_valid():
        form.save(commit=False)
        nouveau_lieu = get_object_or_404(Equipement, id_equip=animal.lieu.id_equip)
        if check_changement(animal.etat,nouveau_lieu.id_equip):
            if nouveau_lieu.disponibilite == "Libre":
                error = False
                ancien_lieu.disponibilite = "Libre"
                ancien_lieu.save()
                form.save()
                capacite = nouveau_lieu.capacite
                occupants = []
                animaux = Character.objects.all().order_by('id_character')
                for animal_x in animaux:
                    if animal_x.lieu.id_equip == nouveau_lieu.id_equip:
                        occupants.append(animal_x.id_character)
                if len(occupants)==capacite:
                    nouveau_lieu.disponibilite = "Occupé"
                else:
                    nouveau_lieu.disponibilite = "Libre"
                nouveau_lieu.save()

                animal.lieu = nouveau_lieu
                nouveau_etat = changement_etat(animal.lieu.id_equip)
                animal.etat = nouveau_etat
                animal.save()
                message = f"{animal.id_character} est dans le lieu démandé ({nouveau_lieu.id_equip})"

                form.save()
                return redirect('animal_detail', id_character=id_character)
            else:
                animal.lieu = ancien_lieu
                animal.save()
                error = True
                occupants = []
                animaux = Character.objects.all().order_by('id_character')
                for animal_x in animaux:
                    if animal_x.lieu.id_equip == nouveau_lieu.id_equip:
                        occupants.append(animal_x.id_character)
                message = f"{nouveau_lieu.id_equip} est deja occupé(e) par {','.join(occupants)}"
        else:
            animal.lieu = ancien_lieu
            animal.save()
            error = True
            message = f"{animal.id_character} ne peut pas aller au lieu demandé ({nouveau_lieu.id_equip}) dans son état actuel ({animal.etat})"
        return render(request,
            'animalerie/animal_detail.html',
            {'animal': animal, 'message': message, 'error': error, 'lieu': ancien_lieu, 'nouveau_lieu': nouveau_lieu, 'form': form})
    else:
        form = ChangeLieuForm()
        return render(request,
            'animalerie/animal_detail.html',
            {'animal': animal, 'lieu': ancien_lieu, 'form': form})
    

def check_capacite(animaux,equipement, nouveau_capacite):
    if nouveau_capacite <= 0:
        return False, "C'est pas possible d'avoir capacité inférieur ou égal à 0"
    else:
        occupants = []
        for animal_x in animaux:
            if animal_x.lieu.id_equip == equipement.id_equip:
                occupants.append(animal_x.id_character)
        qtt_occupants = len(occupants)
        if qtt_occupants == 1:
            text1 = "animal"
        else:
            text1 = "animaux"
        if len(occupants)-nouveau_capacite == 1:
            text2 = "animal"
        else:
            text2 = "animaux"
        if len(occupants)<nouveau_capacite:
            return True, "Libre"
        elif len(occupants)== nouveau_capacite:
            return True, "Occupé"
        else:
            return False, f"{equipement.id_equip} est dejà occupé(e) par {qtt_occupants} {text1} ({','.join(occupants)}). Alors, il faut changer le lieu d’au moins {len(occupants)-nouveau_capacite} {text2} pour pouvoir modifier la capacité de cet emplacement"

def equipement_detail(request, id_equip):
    equipement = get_object_or_404(Equipement, id_equip=id_equip)
    ancien_capacite = equipement.capacite
    occupants = []
    animaux = Character.objects.all().order_by('id_character')
    for animal_x in animaux:
        if animal_x.lieu.id_equip == equipement.id_equip:
            occupants.append(animal_x.id_character)

    form = ChangeCapaciteForm(request.POST, instance=equipement)
    error = None
    message = ""

    if request.method == "POST"and form.is_valid():
        form.save(commit=False)
        nouveau_capacite = equipement.capacite
        print(nouveau_capacite)
        check, message = check_capacite(animaux,equipement, nouveau_capacite)
        if check:
            equipement.disponibilite = message
            equipement.save()
            form.save()

            return redirect('equipement_detail', id_equip=id_equip)
        else:
            equipement.capacite = ancien_capacite
            error = True
            return render(request,
                'animalerie/equipement_detail.html',
                {'equipement': equipement, 'message': message, 'error': error, 'form': form, 'occupants': occupants})
    else:
        form = ChangeCapaciteForm()
        return render(request,
            'animalerie/equipement_detail.html',
            {'equipement': equipement, 'form': form, 'occupants': occupants})