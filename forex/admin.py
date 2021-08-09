from django.contrib import admin
from .models import *
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_value', 'max_value',
                    'bundle_per', 'referral_per', 'referral_breakeven_lvl']
    list_display_links = ['name']
    fieldsets = (
        (None, {
            "fields": (
                ('name'),
                ('min_value', 'max_value'),
                ('bundle_per'),
            ),
        }),
        ('Referal Section', {
            'fields': (
                ('referral_per'),
                ('referral_breakeven_lvl'),
            ),
        }),
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_id', 'Name', 'Age', 'email', 'mobile', 'account_type',
                    'date_of_investment', 'bundle', 'VodCash', 'last_contacted']
    list_display_links = ['account_id']
    list_filter = [('date_of_investment', DateRangeFilter), 'bundle']
    search_fields = ['account_id']
    fieldsets = (
        ('Personal Information', {
            "fields": (
                ('first_name', 'mid_name', 'last_name'),
                ('date_of_birth'),
                ('email', 'mobile'),
                ('national_id'),
                ('address'),
            ),
        }),
        ('Investment Information', {
            "fields": (
                ('account_type', 'date_of_investment'),
                ('vod_cash_number'),
                ('last_contacted'),
                ('comment'),
            ),
        }),
    )


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ['account', 'main_wallet_EGP', 'main_wallet_USD',
                    'Current_Balance', 'trading_result_last_week', 'total_achievement']
    search_fields = ['account']

    # def has_add_permission(self, request):
    #     return False

    # def has_change_permission(self, *args, **kwargs):
    #     return False

    # def has_delete_permission(self, *args, **kwargs):
    #     return False


# @admin.register(TransactionType)
# class TransactionTypeAdmin(admin.ModelAdmin):
#     list_display = ['name']
#     search_fields = ['type', 'name']


# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ['id', 'account', 'channel', 'type',
#                     'amount_EGP', 'deliverd_rate', 'real_rate', 'amount_USD', 'active', 'paid']
#     list_filter = ['transaction_type', 'transaction_type__type', 'active', 'paid']
#     search_fields = ['id', 'account__account_id']
#     autocomplete_fields = ['account', 'transaction_type']
#     fieldsets = (
#         (None, {
#             "fields": (
#                 ('account', 'transaction_type'),
#                 ('amount_EGP', 'deliverd_rate', 'real_rate', 'amount_USD'),
#                 ('active', 'paid'),
#             ),
#         }),
#     )


# @admin.register(Referral)
# class ReferralAdmin(admin.ModelAdmin):
#     list_display = ['id', 'customer', 'referred_by',
#                     'referral_bonus', 'bonus_trans']
#     autocomplete_fields = ['customer', 'referred_by']
#     search_fields = ['id']
#     # fieldsets = (
#     #     (None, {
#     #         "fields": (
#     #             ('customer'),
#     #             ('referred_by'),
#     #         ),
#     #     }),
#     # )


# @admin.register(TotalAsset)
# class TotalAssetAdmin(admin.ModelAdmin):
#     list_display = ['total_USD', 'total_EGP']


# @admin.register(Share)
# class ShareAdmin(admin.ModelAdmin):
#     list_display = ['account', 'share']
#     search_fields = ['account__account_id']

#     # def has_add_permission(self, request):
#     #     return False

#     # def has_change_permission(self, *args, **kwargs):
#     #     return False

#     # def has_delete_permission(self, *args, **kwargs):
#     #     return False


# @admin.register(SharePL)
# class SharePLAdmin(admin.ModelAdmin):
#     list_display = ['share', 'share_cut', 'bundle_cut', 'account_cut']
#     search_fields = ['share__account__account_id']


# @admin.register(FinanceType)
# class FinanceTypeAdmin(admin.ModelAdmin):
#     list_display = ['name']
#     search_fields = ['name']


# @admin.register(CompanyFinance)
# class CompanyFinanceAdmin(admin.ModelAdmin):
#     list_display = ['id', 'finance_type', 'amount']
#     list_filter = ['finance_type']
#     search_fields = ['id']


# @admin.register(Stockholder)
# class StockholderAdmin(admin.ModelAdmin):
#     list_display = ['account', 'profit_share_per', 'PL_balance']
#     search_fields = ['account__account_id']
