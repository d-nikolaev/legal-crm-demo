from django import forms
from .models import CaseEvent, Client, Case
from crispy_forms.helper import FormHelper

class QuickCaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['title', 'client', 'defendant', 'start_date', 'status']
        widgets = {
            # Важно: format='%Y-%m-%d' позволяет браузеру отобразить дату в input type="date"
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        
        # Фильтруем выпадающие списки участников
        self.fields['client'].queryset = Client.objects.filter(role='plaintiff')
        self.fields['defendant'].queryset = Client.objects.filter(role='defendant')
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'role', 'phone', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'