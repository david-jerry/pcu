from datetime import datetime
from operator import attrgetter
from itertools import groupby
from decimal import Decimal
from typing import Any, Dict, Optional
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, CreateView

from apps.accounts.forms import TransferFunds, UserRegistrationForm, AddAccountForm
from django.contrib.auth.views import LogoutView

from apps.accounts.models import Credits, CustomUser, Documents, UserAccount, UserCard, UserCardHistory


class CustomLogoutView(LogoutView):
    next_page = '/'


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = "/"

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user and not user.is_active:
            messages.error(request, "Your account is not active.")
            return None
        return user

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Session will expire when the browser is closed
            self.request.session.set_expiry(0)
        return super().form_valid(form)


class CustomUserRegistrationView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(request.POST['password'])
            user.save()
            return redirect('accounts:login')
        return render(request, self.template_name, {'form': form})


def blocked(request):
    return render(request, 'accounts/blocked.html')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/forget_password.html'
    success_url = reverse_lazy('home')


class UserDetail(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/detail.html'
    pk_url_kwarg = "id"
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not request.user.is_active or not request.user.can_transfer or request.user.account_frozen:
            return redirect('accounts:blocked')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['cards'] = UserCard.objects.filter(user=self.request.user)[:3]
        context['credits'] = Credits.objects.filter(user=self.request.user)[:6]
        context['accounts'] = UserAccount.objects.filter(
            user=self.request.user)[:3]
        context['first_account'] = UserAccount.objects.first()
        return context


class UserDocumentsDetail(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/documents.html'
    pk_url_kwarg = "id"
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not request.user.is_active or not request.user.can_transfer or request.user.account_frozen:
            return redirect('accounts:blocked')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['cards'] = UserCard.objects.filter(user=self.request.user)[:3]
        context['credits'] = Credits.objects.filter(user=self.request.user)[:6]
        context['accounts'] = UserAccount.objects.filter(
            user=self.request.user)[:3]
        context['first_account'] = UserAccount.objects.first()
        context['documents'] = Documents.objects.all()
        return context


class UserCardHistoryView(LoginRequiredMixin, DetailView):
    model = UserCard
    template_name = 'accounts/card_history.html'
    pk_url_kwarg = "id"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not request.user.is_active or not request.user.can_transfer or request.user.account_frozen:
            return redirect('accounts:blocked')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cards'] = UserCard.objects.filter(user=self.request.user)[:3]
        records = UserCardHistory.objects.filter(
            card=self.get_object()).order_by('-timestamp')[:50]
        context['histories'] = records
        return context


class AddAccount(LoginRequiredMixin, CreateView):
    template_name = "accounts/add_account.html"
    form_class = AddAccountForm

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the user to the form instance
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('accounts:detail', kwargs={'id': self.request.user.id})


class PerformTransfer(LoginRequiredMixin, View):
    template_name = 'accounts/transfer.html'

    def get(self, request):
        form = TransferFunds()
        card_id = request.GET.get('card_id') or None
        international = request.GET.get('international') or False
        accounts = UserAccount.objects.filter(user=request.user)
        
        has_card = request.GET.get('has_card') or False
        if (has_card != 'False' or has_card == True) and has_card:
            card = UserCard.objects.get(id=card_id)
        else:
            card = None
        transaction_type = request.GET.get('transaction_type')
        return render(request, self.template_name, {
                                                        'form': form, 
                                                        'card': card, 
                                                        'account': accounts.first(),  
                                                        'accounts': accounts,
                                                        'transaction_type': transaction_type, 
                                                        'has_card': has_card, 
                                                        'international': international
                                                    })

    def post(self, request):
        # querystrings
        card_id = request.POST.get('account_id')
        account = UserAccount.objects.get(id=int(card_id))
        transaction_type = request.POST.get('transaction_type')
        card = UserCard.objects.get(account=int(card_id))
        amount = request.POST.get('amount')

        # Process the form data and perform the transfer logic
        receiver_name = request.POST['receiver_name']
        receiver_account_number = request.POST['receiver_account_number']
        reason = request.POST['reason']
        
        if not request.user.can_transfer:
            messages.info(
                request, "Account temporarily blocked due to suspicious transactions ongoing. Please contact your account manager.")
            return redirect(reverse('accounts:blocked'))

        if transaction_type in [UserCardHistory.TRANSFER, UserCardHistory.WITHDRAWAL, UserCardHistory.TOP_UP]:
            if Decimal(amount) > card.account.balance:
                print("balance insufficient")
                messages.info(request, "Insufficient Balance")
                return redirect(reverse('accounts:transfer'))

        if Decimal(amount) > card.daily_limit:
            print("transaction limit")
            messages.info(
                request, f"Transaction Limit Exceeded: {card.daily_limit}")
            return redirect(reverse('accounts:transfer'))

        user_card_account_numbers = list(request.user.user_accounts.values_list('account_number', flat=True))
        if receiver_account_number in user_card_account_numbers and not (request.user.first_name in receiver_name or request.user.last_name in receiver_name):
            print("wrong recipient")
            messages.info(
                request, "Wrong Recipient Sending Sending to self")
            return redirect(reverse('accounts:transfer'))

        card.card_balance -= Decimal(amount)
        account.balance -= Decimal(amount)
        card.save(update_fields=['card_balance'])
        account.save(update_fields=['balance'])
        messages.info(request, f"{transaction_type.title} Successful")

        # Process transfer logic here
        UserCardHistory.objects.create(
            card=card,
            transaction_type=transaction_type,
            receiver_name=receiver_name,
            receiver_account_number=receiver_account_number,
            reason=reason,
            amount=amount,
            timestamp=datetime.now()
        )

        redirect_url = reverse('accounts:card', kwargs={
                                'id': card.id})
        return redirect(redirect_url)

