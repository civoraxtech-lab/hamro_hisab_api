
from db import db
from db.models import Transaction, Group, Liability, GroupMember
from sqlalchemy.orm import joinedload

class DashboardController:
    @staticmethod
    def index(user):
        """
        Gathers recent transactions (personal + group) and active groups.
        """
        # 1. Fetch 5 Recent Transactions where user is involved
        # We use joinedload to prevent N+1 query issues for categories/groups
        # recent_txs = (
        #     Transaction.query
        #     .join(Liability)
        #     .join(Profile, Liability.profile_id = Profile.id)
        #     .filter(
        #         Profile.user_id == User.id, 
        #         Profile.is_default == True,
        #         Liability.profile_id = Profile.id
        #     )
        #     .options(joinedload(Transaction.category), joinedload(Transaction.group))
        #     .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        #     .limit(5)
        #     .all()
        # )

        # # 2. Fetch 5 Recent Groups user is a member of
        # recent_groups = (
        #     Group.query
        #     .join(GroupMember)
        #     .join(Profile, GroupMember.profile_id = Profile.id)
        #     .filter(GroupMember.profile_id == Profile.id)
        #     .order_by(Group.updated_at.desc())
        #     .limit(5)
        #     .all()
        # )

        # # 3. Format the Response
        # return {
        #     "recent_transactions": [
        #         {
        #             "id": str(tx.id),
        #             "title": tx.title,
        #             "amount": float(tx.amount),
        #             "date": tx.date.isoformat(),
        #             "category": tx.category.name if tx.category else "Uncategorized",
        #             "icon": tx.category.icon,
        #             "group_name": tx.group.name if tx.group else "Personal",
        #             "is_group": tx.group_id is not None
        #         } for tx in recent_txs
        #     ],
        #     "recent_groups": [
        #         {
        #             "id": str(g.id),
        #             "name": g.name,
        #             "icon": g.icon or "👥",
        #             "member_count": len(g.members)
        #         } for g in recent_groups
        #     ]
        # }