from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserAccount, UserCard, CustomUser
import random

def luhn_algorithm(card_number):
    digits = [int(x) for x in card_number]
    checksum = sum(digits[-2::-2] + [sum(divmod(d * 2, 10)) for d in digits[::-2]]) % 10
    return checksum == 0

def generate_debit_card_number(model):
    queryset = model.objects.all()

    while True:
        card_number = ''.join(str(random.randint(0, 9)) for _ in range(16))
        if luhn_algorithm(card_number) and not queryset.filter(card_number=card_number).exists():
            return card_number

def generate_unique_account_number(model):
    queryset = model.objects.all()

    while True:
        number = random.randint(10**11, 10**12 - 1)
        if not queryset.filter(account_number=number).exists():
            return number

def generate_random_3_digit_number():
    return random.randint(100, 999)

def generate_user_card_data(user_card_instance):
    user_card_instance.card_name = user_card_instance.user.get_full_name()
    user_card_instance.card_cvv = generate_random_3_digit_number()
    user_card_instance.card_number = generate_debit_card_number(UserCard)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserAccount.objects.create(user=instance)

@receiver(post_save, sender=UserAccount)
def create_account_number(sender, instance, created, **kwargs):
    if created:
        UserCard.objects.create(user=instance.user, account=instance)
        instance.account_number = generate_unique_account_number(UserAccount)
        instance.save(update_fields=['account_number'])

@receiver(post_save, sender=UserCard)
def create_card_number(sender, instance, created, **kwargs):
    if created:
        generate_user_card_data(instance)
        instance.save(update_fields=['card_number', 'card_name', 'card_cvv'])
