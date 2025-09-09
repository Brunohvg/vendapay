from re import A
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm, SellerForm
from .utils import is_administrador
from django.views.generic import CreateView
from .models import Account


# 🔐 Login personalizado
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'          # Template do login
    redirect_authenticated_user = True             # Redireciona se já estiver logado
    form_class = LoginForm                         # Form customizado

    def form_invalid(self, form):
        """Mensagem de erro caso login falhe"""
        messages.error(self.request, 'Usuário ou senha inválidos.', extra_tags='danger')
        return super().form_invalid(form)
    
    def get_success_url(self):
        """Redireciona para o dashboard após login"""
        return reverse_lazy('dashboard:dashboard')


# 🔓 Logout personalizado
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')    # Redireciona para login após logout

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Você saiu com sucesso.')
        return super().dispatch(request, *args, **kwargs)


# 🛠️ Página de cadastro equipe
class CreateTeamMemberView(CreateView):
    model = Account
    form_class = SellerForm
    template_name = 'accounts/equipe.html'
    context_object_name = 'form'
    
    success_url = reverse_lazy('accounts:equipe')

    def form_valid(self, form):
        messages.success(self.request, 'Membro da equipe criado com sucesso.')
        return super().form_valid(form)