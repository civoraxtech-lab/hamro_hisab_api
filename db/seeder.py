import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from .database import db
from .models import *
from flask_bcrypt import Bcrypt

fake = Faker()
bcrypt = Bcrypt()

def seed_data():
    print("Starting Seeder")
    roles = [Role(name=n) for n in ['ADMIN', 'MEMBER']]
    t_types = [TransactionType(name=n) for n in ['EXPENSE', 'SETTLEMENT', 'ADJUSTMENT']]
    sub_types = [
        SubscriptionType(name='Monthly Basic', price=499.00),
        SubscriptionType(name='Yearly Pro', price=4999.00)
    ]
    categories = [
        Category(name=n, is_default=True, icon="default_icon", iconColor="#000000") 
        for n in ['Food', 'Rent', 'Travel', 'Shopping', 'Others']
    ]

    db.session.add_all(roles + t_types + sub_types + categories)
    db.session.flush()

    # 2. Generate 1,000 Users
    users = []
    profiles = []
    hashed_password = bcrypt.generate_password_hash("password123").decode('utf-8'),
    for _ in range(1000):
        user = User(
            firstname=fake.first_name(),
            lastname=fake.last_name(),
            email=fake.unique.email(),
            password = hashed_password,
            phone=fake.unique.phone_number()[:20],
            code=fake.bothify(text='USR-####')
        )
        users.append(user)
    
    db.session.add_all(users)
    db.session.flush()
    print(f"✅ {len(users)} Users created.")

    for user in users:
        profile = Profile(
            user_id = user.id,
            name = "Home",
            is_default = True
        )
        profiles.append(profile)
    db.session.add_all(profiles)
    db.session.flush()
    print(f"✅ {len(profiles)} Profiles created.")

    # 3. Randomize Subscriptions for some users
    for user in random.sample(users, 300):
        sub = Subscription(
            user_id=user.id,
            type_id=random.choice(sub_types).id,
            expiry=datetime.utcnow() + timedelta(days=365),
            total_amount=5000,
            paid_amount=5000
        )
        db.session.add(sub)

    # 4. Create Groups and Memberships
    # We'll create 150 groups, each with 3-8 members
    for _ in range(150):
        owner = random.choice(profiles)
        new_group = Group(
            name=f"{fake.city()} Squad",
            description=fake.sentence(),
            created_by=owner.id
        )
        db.session.add(new_group)
        db.session.flush()

        # Add 3-8 members to this group
        group_size = random.randint(3, 8)
        members = random.sample(profiles, group_size)
        if owner not in members: members.append(owner)

        for member in members:
            is_admin = (member.id == owner.id)
            gm = GroupMember(
                profile_id=member.id,
                group_id=new_group.id,
                role_id=roles[0].id if is_admin else roles[1].id # Admin or Member
            )
            db.session.add(gm)
        
        # 5. Create Transactions & Liabilities for this group
        for _ in range(random.randint(5, 15)):
            payer = random.choice(members)
            total_amt = random.randint(500, 5000)
            
            trans = Transaction(
                category_id=random.choice(categories).id,
                group_id=new_group.id,
                type_id=t_types[0].id, # Expense
                title=fake.word().capitalize() + " Expense",
                amount=total_amt,
                date=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(trans)
            db.session.flush()

            # Create Liabilities (Split the bill)
            split_amt = total_amt / len(members)
            for m in members:
                liab = Liability(
                    transaction_id=trans.id,
                    profile_id=m.id,
                    settlement_amount=split_amt,
                    initial_payer=(m.id == payer.id),
                    is_verified=True
                )
                db.session.add(liab)

    db.session.commit()
    print("🏁 Mega Seed Complete! Database is now full and ready for testing.")