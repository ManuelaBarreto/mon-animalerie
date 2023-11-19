from django import forms
from .models import Character, Equipement


class ChangeLieuForm(forms.ModelForm):
    
    class Meta:
        model = Character
        fields = ('lieu',)

class ChangeCapaciteForm(forms.ModelForm):
    
    class Meta:
        model = Equipement
        fields = ('capacite',)