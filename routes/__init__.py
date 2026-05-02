# member namespaces
from .member.auth import auth_ns
from .member.users import users_ns
from .member.profiles import profiles_ns
from .member.categories import categories_ns
from .member.group import group_ns
from .member.transaction_types import transaction_types_ns
from .member.liabilities import liabilities_ns
from .member.subscriptions import subscriptions_ns
from .member.subscription_types import subscription_types_ns
from .member.subscription_codes import subscription_codes_ns
from .member.roles import roles_ns
from .member.invitations import invitations_ns

# personal namespaces
from .personal.dashboard import personal_ns
from .personal.transactions import transactions_ns
from .personal.settings import settings_ns

# admin namespaces
from .admin.categories import admin_categories_ns
from .admin.groups import admin_groups_ns
from .admin.roles import admin_roles_ns
from .admin.liabilities import admin_liabilities_ns
from .admin.subscriptions import admin_subscriptions_ns
from .admin.subscription_types import admin_sub_types_ns
from .admin.subscription_codes import admin_sub_codes_ns
from .admin.transaction_types import admin_tx_types_ns
from .admin.users import admin_users_ns
