import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from django_tenants.utils import schema_context
from faker import Faker

from AuthBillet.utils import get_or_create_user
from actions.models import Tag, Action, FundingNeed, Compensation, Participation, Vote, Funding, Comment
from fedow_connect.models import AssetFromFedow


class Command(BaseCommand):
    help = 'Generate mock data for the actions app'

    @atomic
    def handle(self, *args, **kwargs):
        with schema_context('lespass'):
            fake = Faker()
            # Create some Users

            users = [get_or_create_user(email=f'user{i}@example.com', send_mail=False) for i
                     in range(10)]

            # Create some Tags
            tags = [Tag.objects.get_or_create(name=fake.word(), description=fake.text()) for _ in range(10)]

            # Create some Actions
            actions = []
            for _ in range(20):
                action = Action.objects.create(
                    name=fake.sentence(nb_words=5),
                    description=fake.text(),
                    event=None,  # Assuming you have an Event model to be referenced
                    accepts_vote=fake.boolean(),
                    is_fundable=fake.boolean(),
                    required_duration=timedelta(days=random.randint(1, 30)),
                    parent=random.choice([None] + actions)
                )
                actions.append(action)

            # Create FundingNeeds
            for action in actions:
                for _ in range(5):
                    FundingNeed.objects.create(
                        action=action,
                        target=fake.random_number(digits=5),
                        funded_amount=fake.random_number(digits=4),
                        asset=AssetFromFedow.objects.get_or_create(
                            name='FED', currency_code='FED', category='FED')[0]
                    )

            # Create Compensations
            for action in actions:
                for _ in range(3):
                    Compensation.objects.create(
                        action=action,
                        amount=fake.random_number(digits=4),
                        currency=AssetFromFedow.objects.get_or_create(
                            name='FED', currency_code='FED', category='FED')[0]
                    )

            # Create Participations
            for user in users:
                for action in random.sample(actions, k=5):
                    Participation.objects.create(
                        user=user,
                        action=action,
                        time_invested=timedelta(days=random.randint(1, 30)),
                        is_admin_approved=fake.boolean()
                    )

            # Create Votes
            for user in users:
                for action in random.sample(actions, k=5):
                    Vote.objects.create(
                        action=action,
                        voter=user,
                        vote_value=random.choice([-1, 1]),
                        vote_date=fake.date_time_this_year()
                    )

            # Create Fundings
            for action in actions:
                for user in random.sample(users, k=5):
                    Funding.objects.create(
                        action=action,
                        contributor=user,
                        amount=fake.random_number(digits=3),
                        currency=AssetFromFedow.objects.get_or_create(
                            name='FED', currency_code='FED', category='FED')[0],
                        date_contributed=fake.date_time_this_year()
                    )

            # Create Comments
            for action in actions:
                for user in users:
                    Comment.objects.create(
                        action=action,
                        author=user,
                        text=fake.text(),
                        created_at=fake.date_time_this_year()
                    )

        self.stdout.write(self.style.SUCCESS('Successfully generated mock data'))
