from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


class Ingreso(forms.Form):
	matricula=forms.CharField(max_length=7)
	user=forms.CharField(max_length=10)


