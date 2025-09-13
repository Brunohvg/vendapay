from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, View
from django.contrib import messages
from .forms import LoginForm, SellerForm
from .models import Account
from .utils import is_administrador, is_vendedor


# 🔐 Login personalizado
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = LoginForm

    def form_invalid(self, form):
        messages.error(self.request, 'Usuário ou senha inválidos.', extra_tags='danger')
        return super().form_invalid(form)

    def get_success_url(self):
        user = self.request.user

        # 🔁 Redirecionamento baseado no perfil
        if is_vendedor(user):
            return reverse_lazy('dashboard:vendedor_dashboard')  # ← Substitua pelo nome real da URL
        else:
            return reverse_lazy('dashboard:dashboard')  # Padrão para administradores ou outros



# 🔓 Logout personalizado
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Você saiu com sucesso...')
        return super().dispatch(request, *args, **kwargs)


# 🛠️ Página de cadastro equipe (via CreateView)
class CreateTeamMemberView(CreateView):
    model = Account
    form_class = SellerForm
    template_name = 'accounts/equipe.html'
    success_url = reverse_lazy('accounts:equipe')

    def form_valid(self, form):
        messages.success(self.request, 'Membro da equipe criado com sucesso.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Erro ao criar membro da equipe. Verifique os dados e tente novamente.',
            extra_tags='danger'
        )
        return super().form_invalid(form)


# 👥 Página de equipe (via View personalizada)
@method_decorator([login_required, user_passes_test(is_administrador, login_url=reverse_lazy('dashboard:dashboard'))], name='dispatch')
class EquipeView(View):
    template_name = 'accounts/equipe.html'

    def get(self, request, *args, **kwargs):
        form = SellerForm()
        membros = Account.objects.all()
        return render(request, self.template_name, {'form': form, 'membros': membros})

    def post(self, request, *args, **kwargs):
        form = SellerForm(request.POST)
        membros = Account.objects.all()
        if form.is_valid():
            form.save()
            messages.success(request, 'Membro da equipe criado com sucesso.')
            form = SellerForm()  # Limpa o formulário após o sucesso
        else:
            messages.error(
                request,
                'Erro ao criar membro da equipe. Verifique os dados e tente novamente.',
                extra_tags='danger'
            )
        return render(request, self.template_name, {'form': form, 'membros': membros})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

class MeuPerfilView(View):
    template_name = 'accounts/meu_perfil.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'user': request.user
        })  
    
    
    