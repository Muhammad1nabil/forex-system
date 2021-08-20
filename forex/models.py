from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.expressions import F
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum


class TimestampedModel(models.Model):
    """
    Abstract model to contain information about creation/update time.

    :created_at: date and time of record creation.
    :updated_at: date and time of any update happends for record.
    """

    created_at = models.DateTimeField(
        verbose_name='Creation Date/Time', auto_now_add=True)
    updated_at = models.DateTimeField(
        verbose_name='Update Date/Time', auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at', '-updated_at']


class AccountType(TimestampedModel):
    """
    A model to contain information about account type.

    :name: Account type name.
    """

    name = models.CharField(verbose_name='Name',
                            max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class Bundle(TimestampedModel):
    """
    A model to contain information about bundle.

    :name: Bundle name.
    :min_value: Minimum value of a bundle range.
    :max_value: Maximum value of a bundle range.
    :bundle_per: Bundle percentage.
    :referral_per: Referral percentage which a account gets.
    :referral_breakeven_lvl: Referral breakeven level which a referral is active to transfer.
    """

    name = models.CharField(verbose_name='Name', max_length=50, unique=True)
    min_value = models.PositiveSmallIntegerField(verbose_name='Minimum Value')
    max_value = models.PositiveSmallIntegerField(verbose_name='Maximum Value')
    bundle_per = models.FloatField(verbose_name='Bundle Percentage %')
    referral_per = models.FloatField(verbose_name='Referral Percentage %')
    referral_breakeven_lvl = models.FloatField(
        verbose_name='Referral Breakeven Level %')

    def __str__(self):
        return self.name


class Account(TimestampedModel):
    """
    A model to contain information about account.

    :account_id: Account's custom ID.
    :first_name: Account's first name.
    :mid_name: Account's middle name.
    :last_name: Account's last name.
    :date_of_birth: Account's date of birth.
    :email: Account's email.
    :national_id: Account's national ID image.
    :mobile: Account's mobile number.
    :address: Account's address.
    :account_type: A connection to AccountType model. Account's Type in the system.
    :date_of_investment: Date when account started investing.
    :bundle: A connection to Bundle model. Bundle which a account belongs to.
    :vod_cash_number: Account's vodafone cash mobile number.
    :last_contacted: Date and time of last contact with a account.
    :comment: System comment on a account.
    """

    account_id = models.CharField(
        verbose_name='Account ID', editable=False, max_length=50, blank=True, null=True)
    first_name = models.CharField(verbose_name='First Name', max_length=50)
    mid_name = models.CharField(
        verbose_name='Middle Name', max_length=50, blank=True, null=True)
    last_name = models.CharField(verbose_name='Last Name', max_length=50)
    date_of_birth = models.DateField(
        verbose_name='Date of Birth', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', max_length=254)
    national_id = models.ImageField(
        upload_to='nationalIDs', verbose_name='National ID', blank=True, null=True)
    mobile = PhoneNumberField(verbose_name='Mobile Number')
    address = models.CharField(
        verbose_name='Address', max_length=250, blank=True, null=True)
    account_type = models.ForeignKey(
        AccountType, verbose_name='Account Type', on_delete=models.CASCADE)
    date_of_investment = models.DateField(verbose_name='Date of Investment')
    bundle = models.ForeignKey(
        Bundle, verbose_name='Bundle', on_delete=models.CASCADE, max_length=50, blank=True, null=True)
    vod_cash_number = PhoneNumberField(
        verbose_name='Vodafone Cash Mobile Number', blank=True, null=True)
    last_contacted = models.DateTimeField(
        verbose_name='Last Contact', blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    @property
    def Name(self):
        f = f'{self.first_name[0].upper()}{self.first_name[1:]}'
        l = f'{self.last_name[0].upper()}{self.last_name[1:]}'
        if self.mid_name:
            m = f'{self.mid_name[0].upper()}'
            return f'{f} {m}. {l}'
        else:
            return f'{f} {l}'

    @property
    def VodCash(self):
        if self.vod_cash_number:
            return True
        else:
            return False

    @property
    def Age(self):
        import datetime
        age = int((datetime.date.today() - self.date_of_birth).days / 365.25)
        return age

    def __str__(self):
        return f'{self.account_id} | {self.Name}'

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        self.account_id = self.account_type.name[0].upper() + str(self.id)
        return super().save(*args, **kwargs)


class Balance(TimestampedModel):
    """
    A model to contain information about account's balance.

    :account: A connection to Account model. account's balance.
    :main_wallet_EGP: Account's main wallet in EGP.
    :main_wallet_USD: Account's main wallet in USD.
    :balance: Account's balance in USD.
    :trading_result_last_week: Account's last week trading result.
    :total_achievement: Account's total profit/loss (combined).
    """

    account = models.OneToOneField(
        Account, verbose_name='Account', on_delete=models.CASCADE)
    main_wallet = models.FloatField(
        verbose_name='Main Wallet', default=0)
    balance = models.FloatField(verbose_name='Current Balance', default=0)
    trading_result_last_week = models.FloatField(
        verbose_name='Trading Result Last Week', editable=False, default=0)
    PL = models.FloatField(verbose_name='Profit/Loss', default=0)
    total_achievement = models.FloatField(
        verbose_name='Total Achievement', editable=False, default=0)
    share = models.FloatField(
        verbose_name='Share Percentage', default=0)
    profit_per = models.FloatField(
        verbose_name='Profit Percentage', default=0)

    @property
    def Current_Balance(self):
        return f'{self.balance} $'

    @property
    def Main_Wallet(self):
        return f'{self.main_wallet} $'

    @property
    def Last_Week_Percentage(self):
        if self.balance - self.trading_result_last_week != 0:
            return f'{round(self.trading_result_last_week / (self.balance - self.trading_result_last_week), 2)}%'
        else:
            return '--%'

    @property
    def Total_Achievement_Percentage(self):
        if self.main_wallet != 0:
            return f'{self.total_achievement / self.main_wallet}%'
        else:
            return '--%'

    @property
    def Share_Percentage(self):
        return f'{round(self.share * 100, 2)}%'

    def __str__(self):
        return f'{self.account.account_id} {self.account.Name} | {self.balance}$'

    def save(self, *args, **kwargs):
        self.balance = self.main_wallet + self.total_achievement
        self.account.bundle = Bundle.objects.filter(
            min_value__lte=self.main_wallet, max_value__gte=self.main_wallet).first()
        self.profit_per = (100 - self.account.bundle.bundle_per)/100
        if self.balance <= 0:
            self.balance = 0
            self.main_wallet = 0
            self.PL = 0
        self.account.save()
        return super().save(*args, **kwargs)


class TransactionChannel(TimestampedModel):
    """
    A model to contain information about transaction type.

    :name: Transaction type name.
    """

    name = models.CharField(verbose_name='Name', max_length=50, unique=True)

    def __str__(self):
        return f'{self.name}'


class Transaction(TimestampedModel):
    """
    A model to contain information about transaction.

    :account: A conncetion to Account model. Account which a transaction belongs to.
    :transaction_channel: A connection to TransactionChannel model. Channel which a transaction belongs to.
    :transaction_type: Transaction type (Deposit - Withdrawal).
    :amount_EGP: Transaction amount in EGP.
    :rate: USD to EGP rate.
    :amount_USD: Transaction amount in USD.
    :paid: Transaction paid flag.
    :paid_flag: flag if this transaction has been paid and added to the system before.
    """

    TYPE_CHOICES = (
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
    )

    balance = models.ForeignKey(
        Balance, verbose_name='Balance', on_delete=models.CASCADE)
    transaction_channel = models.ForeignKey(
        TransactionChannel, verbose_name='Transaction Type', on_delete=models.CASCADE)
    transaction_type = models.CharField(
        choices=TYPE_CHOICES, verbose_name='Transaction Type', max_length=10)
    amount_EGP = models.FloatField(
        verbose_name='Amount (EGP)', blank=True, null=True)
    amount_USD = models.FloatField(
        verbose_name=' Amount (USD)', blank=True, null=True)
    deliverd_rate = models.FloatField(
        verbose_name='Delivered Rate', help_text='EGP/USD')
    real_rate = models.FloatField(
        verbose_name='Real Rate', help_text='EGP/USD')
    date = models.DateField(
        verbose_name='Transaction Date', default=timezone.now)
    paid = models.BooleanField(verbose_name='Paid', default=False)
    paid_flag = models.BooleanField(
        verbose_name='paid_flag', default=False, editable=False)

    @property
    def type(self):
        return self.transaction_type

    @property
    def channel(self):
        return self.transaction_channel.name

    def clean(self):
        if not self.amount_EGP and not self.amount_USD:
            raise ValidationError({'amount_EGP': 'Transaction must have at least one of (amount EGP - amount USD)',
                                  'amount_USD': 'Transaction must have at least one of (amount EGP - amount USD)'})
        if not self.amount_EGP:
            self.amount_EGP = round(self.amount_USD * self.deliverd_rate, 2)
        if not self.amount_USD:
            self.amount_USD = round(self.amount_EGP / self.deliverd_rate, 2)
        if self.transaction_type.upper() == 'WITHDRAWAL' and self.amount_USD > self.balance.balance:
            raise ValidationError(
                {'amount_USD': 'current balance is lower than the transaction amount'})
        return super().clean()

    def save(self, *args, **kwargs):
        if self.transaction_type.upper() == 'DEPOSIT' and self.paid and not self.paid_flag:
            self.balance.main_wallet += self.amount_USD
            deposit_spread = self.amount_USD - (self.amount_EGP / self.real_rate)
            if deposit_spread > 0:
                type, _ = FinanceType.objects.get_or_create(name='Deposit Spread', type='Revenues')
                CompanyFinance.objects.create(finance_type=type, amount=abs(deposit_spread))
            elif deposit_spread < 0:
                type, _ = FinanceType.objects.get_or_create(name='Deposit Spread', type='Expenses')
                CompanyFinance.objects.create(finance_type=type, amount=abs(deposit_spread))
            self.balance.save()

        if ((self.transaction_type.upper() == 'WITHDRAWAL') and (self.paid and not self.paid_flag)):
            if self.amount_USD > self.balance.main_wallet and self.balance.PL > 0:
                self.balance.PL -= (self.amount_USD - self.balance.main_wallet)
                self.balance.main_wallet = self.balance.PL
                self.balance.PL = 0
            else:
                self.balance.main_wallet -= self.amount_USD
            self.balance.save()

            total_asset = TotalAsset.objects.first()
            total_asset.withdrawals += self.amount_USD
            total_asset.save()
            
            withdrawal_spread = (self.amount_EGP / self.real_rate) - self.amount_USD
            if withdrawal_spread > 0:
                type, _ = FinanceType.objects.get_or_create(name='Withdrawal Spread', type='Revenues')
                CompanyFinance.objects.create(finance_type=type, amount=abs(withdrawal_spread))
            elif withdrawal_spread < 0:
                type, _ = FinanceType.objects.get_or_create(name='Withdrawal Spread', type='Expenses')
                CompanyFinance.objects.create(finance_type=type, amount=abs(withdrawal_spread))

        if self.paid:
            self.paid_flag = True
        return super().save(*args, **kwargs)


class TotalAsset(TimestampedModel):
    """
    A model to contain information about total trading assets.

    :total: Total trading amount
    :PLs: Total trading Profit/Loss amount (difference between self.total and last week total)
    :deposits: Total deposit amounts in last week
    :withdrawals: Total withdrawal amounts in this week
    """

    total = models.FloatField(verbose_name='Total Trading Amount')
    PLs = models.FloatField(verbose_name='Last Week P/L',
                            editable=False, default=0)
    deposits = models.FloatField(
        verbose_name='Total Deposits', default=0, editable=False)
    withdrawals = models.FloatField(
        verbose_name='Total Withdrawals', default=0, editable=False)

    @property
    def Overall_Value(self):
        return f'{self.PLs + self.deposits - self.withdrawals}'

    @property
    def Weekend_Date(self):
        if self.created_at.date().weekday() < 5:
            last_friday = (self.created_at.date()
                           - timedelta(days=self.created_at.weekday())
                           + timedelta(days=4, weeks=-1))
        else:
            last_friday = (self.created_at.date()
                           - timedelta(days=self.created_at.weekday())
                           + timedelta(days=4))
        return last_friday

    def __str__(self):
        return f'{self.total}$'

    old_withdrawals = 0

    def save(self, *args, **kwargs):
        deposits = float()
        # if this the first time save function is called and not the first object
        if not self.id and TotalAsset.objects.first():
            last_total_asset = TotalAsset.objects.first()
            self.PLs = self.total - last_total_asset.total
            # update trading result last week with new account profit cut
            Balance.objects.update(trading_result_last_week=F(
                'share') * F('profit_per') * self.PLs)
            # add trading result last week to total achievement and to PL
            # update balance with new PL values
            Balance.objects.update(total_achievement=F('total_achievement') + F(
                'trading_result_last_week'),
                PL=F('PL') + F('trading_result_last_week'),
                balance=F('PL') + F('main_wallet'))
            # get new deposits to add them to new total asset
            deposits = Transaction.objects.filter(
                created_at__gt=last_total_asset.created_at,
                transaction_type='Deposit',
                paid=True).aggregate(Sum('amount_USD'))['amount_USD__sum']
            self.deposits = round(deposits, 2) if deposits else 0
            self.total += self.deposits
        # if this is the first object
        elif not self.id and not TotalAsset.objects.first():
            self.total = 0
            self.total = Balance.objects.all().aggregate(Sum('main_wallet'))['main_wallet__sum']
            deposits = Transaction.objects.filter(
                transaction_type='Deposit',
                paid=True).aggregate(Sum('amount_USD'))['amount_USD__sum']
            self.deposits = round(deposits, 2) if deposits else 0
            # create share percentage for the first time
            if self.total != 0:
                Balance.objects.update(share=F('balance') / self.total)
            self.total += self.deposits
        if self.old_withdrawals != self.withdrawals:
            self.total -= (self.withdrawals - self.old_withdrawals)
            self.old_withdrawals = self.withdrawals

        # update share percentages according to new balance
        Balance.objects.update(share=F('balance') / self.total)
        return super().save(*args, **kwargs)


class FinanceType(TimestampedModel):
    """
    A model to contain information about finance type.

    :name: Finance type name.
    """
    TYPE_CHOICES = (
        ('Revenues', 'Revenues'),
        ('Expenses', 'Expenses'),
    )
    name = models.CharField(verbose_name='Name', max_length=50)
    type = models.CharField(verbose_name='Type',
                            max_length=50, choices=TYPE_CHOICES)

    def __str__(self):
        return f'{self.name} | {self.type}'
    
    class Meta:
        unique_together = [['name', 'type']]


class CompanyFinance(TimestampedModel):
    """
    A model to contain information about company profit/loss.

    :finance_type: A connection to FinanceType model. Finance type.
    :amount: Finance amount in USD.
    """

    finance_type = models.ForeignKey(
        FinanceType, verbose_name='Finance Type', on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name='Amount USD')



# class Referral(TimestampedModel):
#     """
#     A model to contain information about referral.

#     :customer: A connection to Account model. Customer refered by current account.
#     :referred_by: A connection to Account model. Account which refered to a customer.
#     :referral_bonus: Referral bonus,
#                     referred_by account earns when a customer reaches referral_breakeven_lvl of his bundle.
#     :bonus_trans: A connection to Transaction. Bonus inactive transaction.
#     """

#     customer = models.OneToOneField(
#         Account, related_name='customer', verbose_name='Customer', on_delete=models.CASCADE)
#     referred_by = models.ForeignKey(
#         Account, related_name='referred_by', verbose_name='Referred By', on_delete=models.CASCADE)
#     referral_bonus = models.FloatField(
#         verbose_name='Referral Bonus', blank=True, null=True)
#     bonus_trans = models.OneToOneField(
#         Transaction, verbose_name='Bonus Transaction', on_delete=models.CASCADE, blank=True, null=True)

#     # def __str__(self):
#     #     return f'{self.referred_by.customer_id} -> {self.customer.customer_id}'


# class Share(TimestampedModel):
#     """
#     A model to contain information about account share.

#     :account: A connection to Account model. Share which belongs to an account.
#     :share: Share percentage from total trading asset.
#     """

#     account = models.ForeignKey(
#         Account, verbose_name='Account', on_delete=models.CASCADE)
#     share = models.FloatField(verbose_name='Share %',
#                               editable=False, default=0)

#     def __str__(self):
#         return f'{self.account.Name} | {self.share}'


# ################################################################


# class Stockholder(TimestampedModel):
#     """
#     A model to contain information about stockholder.

#     :account: A connection to Account model. Stockholder's account.
#     :profit_share_per: Stockholder profit share percentage.
#     :PL_balance: Stockholder profit/loss balance in USD.
#     """

#     stackholder_name = models.CharField(verbose_name='Name', max_length=50)
#     profit_share_per = models.FloatField(
#         verbose_name='Profit Share Percentage %')
#     PL_balance = models.FloatField(verbose_name='PL Balance in USD', default=0)

#     def __str__(self):
#         return f'{self.account} | {self.profit_share_per}'


def create_balance(sender, **kwargs):
    if kwargs['created']:
        Balance.objects.create(account=kwargs['instance'])


post_save.connect(create_balance, sender=Account)
