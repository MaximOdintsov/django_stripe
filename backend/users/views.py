from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate
from django import views
from django.contrib.auth import views as auth_views

from .forms import MyRegistrationForm, MyAuthenticationForm

User = get_user_model()


class MyRegistrationView(views.View):
    template_name = 'users/registration.html'

    def get(self, request):
        context = {'form': MyRegistrationForm}
        return render(request, self.template_name, context)

    def post(self, request):
        form = MyRegistrationForm(request.POST)
        if request.method == "POST":
            if form.is_valid():
                form.save()
                email = form.cleaned_data.get('email')
                username = email
                password = form.cleaned_data.get('password2')

                authenticate(username=username, password=password)
                return redirect('home')
            else:
                return render(request, self.template_name, context={'form': form})


class MyLoginView(auth_views.LoginView):
    form_class = MyAuthenticationForm
    template_name = 'users/login.html'
    success_url = 'home'
