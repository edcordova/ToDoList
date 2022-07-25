from django import forms
from django.contrib.auth.models import User
from django.db.models.functions import Lower



class ParticipantsForm(forms.Form):
   
    users = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(),
            queryset = User.objects.all().order_by(Lower('username')))

    # widget=forms.CheckboxSelectMultiple()

   
