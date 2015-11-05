""" Forms for swiftbrowser.browser """
# -*- coding: utf-8 -*-
#pylint:disable=R0924
from django import forms
from django.conf import settings
#from utils import get_keystone_tenants


class CreateContainerForm(forms.Form):
    """ Simple form for container creation """
    containername = forms.CharField(max_length=100)


class PseudoFolderForm(forms.Form):
    """ Upload form """
    foldername = forms.CharField(max_length=100)


class LoginForm(forms.Form):
    """ Login form """
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )


class TimeForm(forms.Form):
    ''' Custom Temp URL Form. Allows users to specify time in hours and
    days.'''
    days = forms.DecimalField(initial=0)
    hours = forms.DecimalField(initial=0)


class CreateUserForm(forms.Form):
    ''' Form for creating new users on Keystone.'''
    email = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)


class DeleteUserForm(forms.Form):
    ''' Form for deleting a user on Keystone.'''
    user_id = forms.CharField(max_length=100)


class UpdateACLForm(forms.Form):
    ''' Form for updating container ACLs'''
    read_acl = forms.CharField(required=False)
    write_acl = forms.CharField(required=False)
