from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from AuthBillet.models import TibilletUser
from BaseBillet.models import Event
from fedow_connect.models import AssetFromFedow


class Tag(models.Model):
    """
    Modèle pour étiqueter les fonctionnalités avec des mots-clés (inspiré de schema.org: Keyword).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Action(models.Model):
    """
    Modèle aligné avec Schema.org, pour gérer des actions et sous-actions avec
    financement, participants, et relations parent/enfant.
    """
    name = models.CharField(
        max_length=255,
        help_text=_("Le nom de l'action.")
    )
    description = models.TextField(
        blank=True,
        help_text=_("La description détaillée de l'action.")
    )

    # Event associé
    event = models.ForeignKey(
        Event,
        null=True,
        related_name="actions",
        on_delete=models.CASCADE,
        help_text=_("Évènement associé"),
    )

    # Accepter les votes ?
    accepts_vote = models.BooleanField(
        default=True,
        help_text=_("Indique si cette action peut recevoir des votes ou non.")
    )

    # Il peut être financé ?
    is_fundable = models.BooleanField(
        default=True,
        help_text=_("Indique si cette action peut recevoir des financements ou non.")
    )

    # Besoin d'une gestion du temps ?
    required_duration = models.DurationField(
        default=0,
        help_text=_("La durée estimée pour compléter cette action.")
    )

    # relation parent / enfant
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        help_text=_("L'action parente de laquelle cette action fait partie, si applicable.")
    )

    def __str__(self):
        return self.name

    # @property
    # def total_votes(self):
    #     return self.votes.aggregate(total=Sum('vote_value'))['total'] or 0

    # @property
    # def is_parent(self):
    #     return self.parent is None


class FundingNeed(models.Model):
    """
    Modèle pour représenter les besoins de financement d'une action,
    avec des noms de variables alignés sur schema.org.
    """

    action = models.ForeignKey(
        'Action',
        on_delete=models.CASCADE,
        related_name="funding_needs",
        help_text=_("L'action pour laquelle le besoin de financement est défini.")
    )
    target = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Le montant total nécessaire pour le financement de cette action."),
        verbose_name=_("totalPaymentDue")  # Schema.org equivalent
    )
    funded_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Le montant déjà financé pour cette action."),
        verbose_name=_("amount")  # Schema.org equivalent
    )
    asset = models.ForeignKey(
        AssetFromFedow,
        on_delete=models.PROTECT,
        related_name="funding_needs",
        help_text=_("L'actif utilisé pour le financement."),
        verbose_name=_("currency")  # Schema.org equivalent
    )

    def __str__(self):
        return f"Besoin de financement pour {self.action.name}: {self.target} {self.asset.name}, financé: {self.funded_amount}"


class Compensation(models.Model):
    """
    Modèle pour représenter la rémunération par heure de travail, aligné avec Schema.org.
    """

    action = models.ForeignKey(
        'Action',
        on_delete=models.CASCADE,
        related_name="compensations",
        help_text=_("L'action pour laquelle la rémunération est spécifiée.")
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Le montant de la rémunération par unité d'heure.")
    )
    currency = models.ForeignKey(
        AssetFromFedow,
        on_delete=models.PROTECT,
        related_name="compensations",
        help_text=_("La monnaie utilisée pour la rémunération.")
    )

    def __str__(self):
        return f"{self.amount} {self.currency.name} pour {self.action.name}"


class Participation(models.Model):
    """
    Modèle pour représenter la participation à une action.
    """
    user = models.ForeignKey(
        TibilletUser,
        on_delete=models.CASCADE,
        related_name="participations",
        help_text=_("L'utilisateur participant à l'action.")
    )
    action = models.ForeignKey(
        'Action',
        on_delete=models.CASCADE,
        related_name="participations",
        help_text=_("L'action à laquelle l'utilisateur participe.")
    )
    time_invested = models.DurationField(
        default=0,
        help_text=_("Le temps passé par l'utilisateur sur cette action.")
    )
    is_admin_approved = models.BooleanField(
        default=False,
        help_text=_("Indique si la participation a été validée par un administrateur.")
    )

    def __str__(self):
        return f"Participation de {self.user.first_name} {self.user.last_name} à {self.action.name}"


class Vote(models.Model):
    """
    Modèle de vote basé sur Schema.org, permettant aux utilisateurs de voter pour une action.
    """
    action = models.ForeignKey(Action, on_delete=models.CASCADE,
                               related_name="votes")  # Cible du vote, nommée `action` pour correspondre au modèle Action
    voter = models.ForeignKey(TibilletUser, on_delete=models.CASCADE, related_name="user_votes")  # Auteur du vote
    vote_value = models.IntegerField(
        default=1)  # Valeur du vote, pouvant être ajustée si un système de points est souhaité
    vote_date = models.DateTimeField(auto_now_add=True)  # Date du vote, enregistrée automatiquement

    class Meta:
        unique_together = ('action', 'voter')  # Empêche un utilisateur de voter plusieurs fois pour la même action

    def __str__(self):
        return f"Vote by {self.voter.first_name} on {self.action.name} (Value: {self.vote_value})"


class Funding(models.Model):
    """
    Modèle pour gérer les contributions financières aux fonctionnalités (inspiré de schema.org: MonetaryAmount).
    """
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name="funding")
    contributor = models.ForeignKey(TibilletUser, on_delete=models.CASCADE, related_name="contributions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_contributed = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey(AssetFromFedow, on_delete=models.CASCADE, related_name="fundings")

    def __str__(self):
        return f"{self.amount} {self.currency} by {self.contributor.first_name} {self.contributor.last_name} for {self.action.name}"


class Comment(models.Model):
    """
    Modèle pour les commentaires sur les fonctionnalités.
    """
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(TibilletUser, on_delete=models.SET_NULL, null=True, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.first_name} on {self.action.name}"
