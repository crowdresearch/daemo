from csp import settings
from django import forms
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    email = forms.EmailField(label='',
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                           'placeholder': 'Email',
                                                           'required': '',
                                                           'id': 'register__email',
                                                           'ng-model': 'register.email',
                                                           'type': 'email',

                                                           })
                             )
    first_name = forms.CharField(label='',
                                 widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'placeholder': 'First Name',
                                                               'required': '',
                                                               'id': 'register__first_name',
                                                               'ng-model': 'register.first_name',
                                                               }))
    last_name = forms.CharField(label='',
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': 'Last Name',
                                                              'required': '',
                                                              'id': 'register__last_name',
                                                              'ng-model': 'register.last_name',

                                                              }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'required': '',
                                                                  'placeholder': 'Password - at least 8 characters long',
                                                                  'id': 'register__password1',
                                                                  'ng-model': 'register.password1',
                                                                  }),
                                label='')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'required': '',
                                                                  'placeholder': 'Confirm Password',
                                                                  'id': 'register__password2',
                                                                  'ng-model': 'register.password2',
                                                                  }),
                                label='')

    def clean(self):
        if settings.REGISTRATION_ALLOWED:
            try:
                if User.objects.filter(email__iexact=self.email):  # cleaned_data['email']
                    raise forms.ValidationError("Email already in use.")
                if len(self.password1) < 8:  # cleaned_data['password1']
                    raise forms.ValidationError("Password needs to be at least eight characters long.")
                if self.password1 != self.password2:  # self.cleaned_data['password1'] != self.cleaned_data['password2']
                    raise forms.ValidationError("The two password fields didn't match.")
                return True
            except KeyError:
                pass
        else:
            raise forms.ValidationError("Currently registrations are not allowed.")


class PasswordResetForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'required': '',
                                                                  'placeholder': 'Password - at least 8 characters long',
                                                                  'id': 'reset_password__password1',
                                                                  'ng-model': 'reset_password.password1',
                                                                  }),
                                label='')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'required': '',
                                                                  'placeholder': 'Confirm Password',
                                                                  'id': 'reset_password__password2',
                                                                  'ng-model': 'reset_password.password2',
                                                                  }),
                                label='')

    def clean(self):
        if settings.PASSWORD_RESET_ALLOWED:
            try:
                if len(self.password1) < 8:  # cleaned_data['password1']
                    raise forms.ValidationError("Password needs to be at least eight characters long.")
                if self.password1 != self.password2:
                    raise forms.ValidationError("The two password fields didn't match.")
                return True
            except KeyError:
                pass
        else:
            raise forms.ValidationError("Currently password resetting is not allowed.")


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='',
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                           'placeholder': 'Email',
                                                           'required': '',
                                                           'id': 'forgot_password__email',
                                                           'ng-model': 'forgot_password.email',
                                                           'type': 'email',
                                                           })
                             )

    def clean(self):
        try:
            if User.objects.filter(email__iexact=self.email):  # cleaned_data['email']
                pass
            else:
                raise forms.ValidationError("Invalid email entered.")
        except KeyError:
            pass
            # raise forms.ValidationError("Invalid email entered.")


class LoginForm(forms.Form):
    form_name = 'login_form'
    email = forms.CharField(label='',
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': 'Email or Username',
                                                          'required': '',
                                                          'ng-model': 'login.username',
                                                          'id': 'login__username',

                                                          })
                            )
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'required': '',
                                                                  'placeholder': 'Password',
                                                                  'ng-model': 'login.password',
                                                                  'id': 'login__password',
                                                                  }),
                                label='')
