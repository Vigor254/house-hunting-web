from django import forms
from .models import SavedSearch


class InquiryMessageForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Type a message..."}),
        label="",
    )


class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        fields = ["room_type", "max_price", "keyword"]
        widgets = {
            "keyword": forms.TextInput(attrs={"placeholder": "e.g. Tudor, Kisauni..."}),
        }
