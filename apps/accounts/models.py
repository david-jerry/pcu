import math
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_active') is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    can_transfer = models.BooleanField(default=True)
    account_frozen = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

class UserAccount(models.Model):
    USD="USD"
    AUD="AUD"
    CAD="CAD"
    CHF="CHF"
    GBP="GBP"
    YEN="YEN"
    AZN="AZN"
    EUR="EUR"
    RUB="RUB"
    AZN="AZN"
    CURRENCY=(
        (USD, USD),
        (AUD, AUD),
        (CAD, CAD),
        (CHF, CHF),
        (GBP, GBP),
        (YEN, YEN),
        (AZN, AZN),
        (EUR, EUR),
        (RUB, RUB),
        (AZN, AZN), 
    )
    
    SAVINGS="SAVINGS"
    CURRENT="CURRENT"
    BUSINESS="BUSINESS"
    PREMIUM="PREMIUM"
    ACCOUNT_TYPE=(
        (SAVINGS, SAVINGS),
        (CURRENT, CURRENT),
        (BUSINESS, BUSINESS),
        (PREMIUM, PREMIUM)
    )
    
    user = models.ForeignKey(CustomUser, verbose_name="user_bank_account", on_delete=models.CASCADE, related_name="user_accounts")
    account_number = models.CharField(max_length=20)
    currency = models.CharField(max_length=4, choices=CURRENCY, default=USD)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE, default=SAVINGS)
    pin = models.CharField(max_length=4, default="0000")
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.email

class UserCard(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name="card_user", on_delete=models.CASCADE, related_name="user_card", null=True, blank=True)
    account = models.ForeignKey(UserAccount, verbose_name="account_number", on_delete=models.CASCADE, related_name="user_card_account_number")
    card_name = models.CharField(max_length=200)
    card_number = models.CharField(max_length=20)
    card_cvv = models.CharField(max_length=3)
    card_pin = models.CharField(max_length=4, default="0000")
    card_type = models.CharField(max_length=20, default="Master")
    card_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    daily_limit = models.DecimalField(max_digits=20, decimal_places=2, default=50000.00)
    monthly_limit = models.DecimalField(max_digits=20, decimal_places=2, default=1000000.00)

    def __str__(self):
        return f"{self.account.user.email} | {self.card_number}"


class UserCardHistory(models.Model):
    DEBIT = "DEBIT"
    TRANSFER = "TRANSFER"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    TOP_UP = "MOBILE_TOP_UP"
    TTYPE = (
        (DEBIT, DEBIT),
        (TRANSFER, TRANSFER),
        (WITHDRAWAL, WITHDRAWAL),
        (TOP_UP, TOP_UP),
        (DEPOSIT, DEPOSIT),
    )
    USD="USD"
    AUD="AUD"
    CAD="CAD"
    CHF="CHF"
    GBP="GBP"
    YEN="YEN"
    AZN="AZN"
    EUR="EUR"
    RUB="RUB"
    AZN="AZN"
    CURRENCY=(
        (USD, USD),
        (AUD, AUD),
        (CAD, CAD),
        (CHF, CHF),
        (GBP, GBP),
        (YEN, YEN),
        (AZN, AZN),
        (EUR, EUR),
        (RUB, RUB),
        (AZN, AZN), 
    )

    card = models.ForeignKey(UserCard, related_name='card_history', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, default=DEBIT, choices=TTYPE)
    receiver_name = models.CharField(max_length=250, default="self")
    receiver_account_number = models.CharField(max_length=20)
    reason = models.CharField(max_length=200)
    currency = models.CharField(max_length=4, choices=CURRENCY, default=USD)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.card.account.user.email} | {self.card.card_number}"

class Credits(models.Model):
    USD="USD"
    AUD="AUD"
    CAD="CAD"
    CHF="CHF"
    GBP="GBP"
    YEN="YEN"
    AZN="AZN"
    EUR="EUR"
    RUB="RUB"
    AZN="AZN"
    CURRENCY=(
        (USD, USD),
        (AUD, AUD),
        (CAD, CAD),
        (CHF, CHF),
        (GBP, GBP),
        (YEN, YEN),
        (AZN, AZN),
        (EUR, EUR),
        (RUB, RUB),
        (AZN, AZN), 
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_credit")
    bank = models.CharField(max_length=500, blank=True)
    title = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=15000.00)
    paid = models.DecimalField(max_digits=20, decimal_places=2, default=1000.00)
    currency = models.CharField(max_length=4, choices=CURRENCY, default=USD)
    debt = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    duration_months = models.IntegerField(default=6)
    
    @property
    def amount_to_be_paid(self):
        monthly_interest_rate = 0.035
        # amount = self.amount * (0.02 * (1 + 0.02)**self.duration_months) / ((1 + 0.02)**self.duration_months - 1)
        numerator = self.amount * (monthly_interest_rate * math.pow((1 + monthly_interest_rate), self.duration_months))
        denominator = math.pow((1 + monthly_interest_rate), self.duration_months) - 1
        amount = numerator / denominator
        return amount 
    
    @property
    def remaining_payment(self):
        amount = self.amount_to_be_paid() * self.duration_months
        return amount - self.paid
    
    @property
    def calculate_percentage_paid(self):
        percentage_paid = (self.paid / self.amount) * 100
        return round(percentage_paid, 2)
    
    
class Documents(models.Model):
    USD="USD"
    AUD="AUD"
    CAD="CAD"
    CHF="CHF"
    GBP="GBP"
    YEN="YEN"
    AZN="AZN"
    EUR="EUR"
    RUB="RUB"
    AZN="AZN"
    CURRENCY=(
        (USD, USD),
        (AUD, AUD),
        (CAD, CAD),
        (CHF, CHF),
        (GBP, GBP),
        (YEN, YEN),
        (AZN, AZN),
        (EUR, EUR),
        (RUB, RUB),
        (AZN, AZN), 
    )
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PENDING = "Pending"
    STATUS = (
        (APPROVED, APPROVED),
        (REJECTED, REJECTED),
        (PENDING, PENDING),
    )
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    status = models.CharField(max_length=15, choices=STATUS, default=APPROVED)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=15000.00)
    currency = models.CharField(max_length=4, choices=CURRENCY, default=USD)

    def __str__(self):
        return self.title