""" Forms for swiftbrowser.browser """
# -*- coding: utf-8 -*-
#pylint:disable=R0924
from django import forms
from django.conf import settings
from utils import get_keystone_tenants


class CreateContainerForm(forms.Form):
    """ Simple form for container creation """
    containername = forms.CharField(max_length=100)


class AddACLForm(forms.Form):
    """ Form for ACLs """
    username = forms.CharField(max_length=100)
    read = forms.BooleanField(required=False)
    write = forms.BooleanField(required=False)


class PseudoFolderForm(forms.Form):
    """ Upload form """
    foldername = forms.CharField(max_length=100)


class LoginForm(forms.Form):
    """ Login form """
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    # OPTIONS = [(k, v) for k, v in get_keystone_tenants().items()]
    # tenant = forms.ChoiceField(choices=OPTIONS)


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )
