from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


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
    :referal_per: Referal percentage which a account gets.
    :referal_breakeven_lvl: Referal breakeven level which a referal is active to transfer.
    """

    name = models.CharField(verbose_name='Name', max_length=50, unique=True)
    min_value = models.PositiveSmallIntegerField(verbose_name='Minimum Value')
    max_value = models.PositiveSmallIntegerField(verbose_name='Maximum Value')
    bundle_per = models.FloatField(verbose_name='Bundle Percentage %')
    referal_per = models.FloatField(verbose_name='Referal Percentage %')
    referal_breakeven_lvl = models.FloatField(
        verbose_name='Referal Breakeven Level %')

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
    :mobile: Account's mobile number.
    :address: Account's address.
    :account_type: A connection to AccountType model. Account's Type in the system.
    :date_of_investment: Date when account started investing.
    :bundle: A connection to Bundle model. Bundle which a account belongs to.
    :vod_cash_number: Account's vodafone cash mobile number.
    :last_contacted: Date and time of last contact with a account.
    :refered_by: A connection to Account model. Another account who refered this account.
    :comment: System comment on a account.
    """

    account_id = models.CharField(
        verbose_name='Account ID', editable=False, max_length=50, blank=True, null=True)
    first_name = models.CharField(verbose_name='First Name', max_length=50)
    mid_name = models.CharField(
        verbose_name='Middle Name', max_length=50, blank=True, null=True)
    last_name = models.CharField(verbose_name='Last Name', max_length=50)
    date_of_birth = models.DateField(verbose_name='Date of Birth')
    email = models.EmailField(verbose_name='Email', max_length=254)
    mobile = PhoneNumberField(verbose_name='Mobile Number')
    address = models.CharField(
        verbose_name='Address', max_length=250, blank=True, null=True)
    account_type = models.ForeignKey(
        AccountType, verbose_name='Account Type', on_delete=models.CASCADE)
    date_of_investment = models.DateField(verbose_name='Date of Investment')
    bundle = models.ForeignKey(
        Bundle, verbose_name='Bundle', on_delete=models.CASCADE)
    vod_cash_number = PhoneNumberField(
        verbose_name='Vodafone Cash Mobile Number', blank=True, null=True)
    last_contact_date = models.DateTimeField(
        verbose_name='Last Contact', blank=True, null=True)
    refered_by = models.ForeignKey(
        Account, verbose_name='Refered By', on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    @property
    def Name(self):
        f = f'{self.first_name[0].cap()}{self.first_name[1:]}'
        l = f'{self.last_name[0].cap()}{self.last_name[1:]}'
        if self.mid_name:
            m = f'{self.mid_name[0].cap()}.'
            return f'{f} {m}.{l}'
        else:
            return f'{f} {l}'

    def __str__(self):
        return f'{self.account_id} | {self.name}'

    def save(self, *args, **kwargs):
        self.account_id = self.account_type.name[0].cap() + str(self.id)
        return super().save(*args, **kwargs)


class TransactionType(TimestampedModel):
    """
    A model to contain information about transaction type.

    :name: Transaction type name.
    """

    name = models.CharField(verbose_name='Name',
                            max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class Transaction(TimestampedModel):
    """
    A model to contain information about transaction.

    :account: A conncetion to Account model. Account which a transaction belongs to.
    :transaction_type: A connection to TransactionType model. Type which a transaction belongs to.
    :amount_EGP: Transaction amount in EGP.
    :rate: USD to EGP rate.
    :amount_USD: Transaction amount in USD.
    """

    account = models.ForeignKey(
        Account, verbose_name='Account', on_delete=models.CASCADE)
    transaction_type = models.ForeignKey(
        TransactionType, verbose_name='Transaction Type', on_delete=models.CASCADE)
    amount_EGP = models.FloatField(
        verbose_name='Amount EGP', blank=True, null=True)
    rate = models.FloatField(verbose_name='USD/EGP rate')
    amount_USD = models.FloatField(
        verbose_name='Amount USD', blank=True, null=True)

    def clean(self):
        if not self.amount_EGP and not self.amount_USD:
            raise ValidationError({'amount_EGP': 'Transaction must have at least one of (amount EGP - amount - USD)',
                                  'amount_USD': 'Transaction must have at least one of (amount EGP - amount - USD)'})
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.amount_EGP:
            self.amount_EGP = self.amount_USD * self.rate
        if not self.amount_USD:
            self.amount_USD = self.amount_EGP / self.rate
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
    main_wallet_EGP = models.FloatField(
        verbose_name='Main Wallet EGP', default=0)
    main_wallet_USD = models.FloatField(
        verbose_name='Main Wallet USD', default=0)
    balance = models.FloatField(verbose_name='Balance USD', default=0)
    trading_result_last_week = models.FloatField(
        verbose_name='Trading Result Last Week', editable=False, blank=True, null=True)
    total_achievement = models.FloatField(
        verbose_name='Total Achievement', editable=False, default=0)

    def __str__(self):
        return f'{self.account.account_id} | {self.balance}$'


class TotalAsset(TimestampedModel):
    """
    A model to contain information about total trading assets.

    :total_USD: Total trading amount in USD
    :total_EGP: Total trading amount in EGP
    """

    total_USD = models.FloatField(verbose_name='Total Trading Amount USD')
    total_EGP = models.FloatField(verbose_name='Total Trading Amount EGP')

    def __str__(self):
        return self.total_USD


class Share(TimestampedModel):
    """
    A model to contain information about account share.

    :account: A connection to Account model. Share which belongs to an account.
    :share: Share percentage from total trading asset.
    """

    account = models.ForeignKey(
        Account, verbose_name='Account', on_delete=models.CASCADE)
    share = models.FloatField(verbose_name='Share %',
                              editable=False, default=0)

    def __str__(self):
        return f'{self.account.name} | {self.share}'

    def save(self, *args, **kwargs):
        total = TotalAsset.objects.filter(id=1).first()
        balance = Balance.objects.get(account=self.account.id).balance
        if total:
            self.share = balance / total * 100
        return super().save(*args, **kwargs)


class SharePL(TimestampedModel):
    """
    A model to contain information about share profit/loss.

    :share: A coonection to Sccount model. Share which a PL belongs to.
    :share_cut: Total share cut.
    :bundle_cut: Bundle cut amount.
    :account_cut: Account cut amount.
    """

    share = models.ForeignKey(
        Share, verbose_name='Share', on_delete=models.CASCADE)
    share_cut = models.FloatField(
        verbose_name='Total Share Cut USD', editable=False)
    bundle_cut = models.FloatField(
        verbose_name='Bundle Cut USD', editable=False)
    account_cut = models.FloatField(
        verbose_name='Account Cut USD', editable=False)

    def __str__(self):
        return f'{self.share} | {self.share_cut}'

    def save(self, *args, **kwargs):
        bundle_per = self.share.account.bundle.bundle_per
        self.bundle_cut = bundle_per / 100 * self.share_cut
        self.account_cut = self.share_cut - self.bundle_cut
        return super().save(*args, **kwargs)


class FinanceType(TimestampedModel):
    """
    A model to contain information about finance type.

    :name: Finance type name.
    """

    name = models.CharField(verbose_name='Name',
                            max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class CompanyFinance(TimestampedModel):
    """
    A model to contain information about company profit/loss.

    :finance_type: A connection to FinanceType model. Finance type.
    :amount: Finance amount in USD.
    """

    finance_type = models.ForeignKey(
        FinanceType, verbose_name='Finance Type', on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name='Amount USD')


class Stockholder(TimestampedModel):
    """
    A model to contain information about stockholder.

    :account: A connection to Account model. Stockholder's account.
    :profit_share_per: Stockholder profit share percentage.
    :PL_balance: Stockholder profit/loss balance in USD.
    """

    account = models.ForeignKey(
        Account, verbose_name='Stockholder Account', on_delete=models.CASCADE)
    profit_share_per = models.FloatField(
        verbose_name='Profit Share Percentage %')
    PL_balance = models.FloatField(verbose_name='PL Balance in USD', default=0)

    # must check profit_share_per all equal 100% before updating any PL_balance

    def __str__(self):
        return f'{self.account} | {self.profit_share_per}'
