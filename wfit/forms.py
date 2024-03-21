from django import forms

from wfit.models import TrelloList


class TrelloListForm(forms.ModelForm):
    class Meta:
        model = TrelloList
        fields = ['workflow_stage']