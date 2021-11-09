import uuid

import requests
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.aggregates import Sum

# Create your models here.
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from solo.models import SingletonModel
from django.utils.translation import ugettext_lazy as _
from stdimage import StdImageField
from stdimage.validators import MaxSizeValidator
from django.db import connection

from QrcodeCashless.models import CarteCashless
from TiBillet import settings
import stripe

import logging

logger = logging.getLogger(__name__)


class OptionGenerale(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=30)
    poids = models.PositiveSmallIntegerField(default=0, verbose_name=_("Poids"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('poids',)
        verbose_name = _('Options Generales')
        verbose_name_plural = _('Options Generales')


@receiver(post_save, sender=OptionGenerale)
def poids_option_generale(sender, instance: OptionGenerale, created, **kwargs):
    if created:
        # poids d'apparition
        if instance.poids == 0:
            instance.poids = len(OptionGenerale.objects.all()) + 1

        instance.save()


class Configuration(SingletonModel):
    organisation = models.CharField(max_length=50, verbose_name=_("Nom de l'organisation"))
    short_description = models.CharField(max_length=250, verbose_name=_("Description courte"))

    adress = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    site_web = models.URLField(blank=True, null=True)

    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)

    adhesion_obligatoire = models.BooleanField(default=False)

    name_required_for_ticket = models.BooleanField(default=False, verbose_name=_("Billet nominatifs"))

    carte_restaurant = StdImageField(upload_to='images/',
                                     null=True, blank=True,
                                     validators=[MaxSizeValidator(1920, 1920)],
                                     variations={
                                         'fhd': (1920, 1920),
                                         'hdr': (720, 720),
                                         'med': (480, 480),
                                         'thumbnail': (150, 90),
                                     },
                                     delete_orphans=True,
                                     verbose_name=_('Carte du restaurant')
                                     )

    img = StdImageField(upload_to='images/',
                        null=True, blank=True,
                        # validators=[MaxSizeValidator(1920, 1920)],
                        variations={
                            'fhd': (1920, 1920),
                            'hdr': (720, 720),
                            'med': (480, 480),
                            'thumbnail': (150, 90),
                        },
                        delete_orphans=True,
                        verbose_name='Background'
                        )

    mollie_api_key = models.CharField(max_length=50,
                                      blank=True, null=True)

    stripe_api_key = models.CharField(max_length=110, blank=True, null=True)
    stripe_test_api_key = models.CharField(max_length=110, blank=True, null=True)
    stripe_mode_test = models.BooleanField(default=True)

    activer_billetterie = models.BooleanField(default=True, verbose_name=_("Activer la billetterie"))

    jauge_max = models.PositiveSmallIntegerField(default=50, verbose_name=_("Jauge maximale"))

    option_generale_radio = models.ManyToManyField(OptionGenerale,
                                                   blank=True,
                                                   related_name="radiobutton")

    option_generale_checkbox = models.ManyToManyField(OptionGenerale,
                                                      blank=True,
                                                      related_name="checkbox")

    server_cashless = models.URLField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name=_("Adresse du serveur Cashless")
    )

    key_cashless = models.CharField(
        max_length=41,
        blank=True,
        null=True,
        verbose_name=_("Clé d'API du serveur cashless")
    )


class Product(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)

    name = models.CharField(max_length=50)

    publish = models.BooleanField(default=False)

    img = StdImageField(upload_to='images/',
                        null=True, blank=True,
                        validators=[MaxSizeValidator(1920, 1920)],
                        variations={
                            'fhd': (1920, 1920),
                            'hdr': (720, 720),
                            'med': (480, 480),
                            'thumbnail': (150, 90),
                        },
                        delete_orphans=True,
                        verbose_name='Image'
                        )

    BILLET, PACK, RECHARGE_CASHLESS, VETEMENT, MERCH, ADHESION = 'B', 'P', 'R', 'T', 'M', 'A'
    TYPE_CHOICES = [
        (BILLET, _('Billet')),
        (PACK, _("Pack d'objets")),
        (RECHARGE_CASHLESS, _('Recharge cashless')),
        (VETEMENT, _('Vetement')),
        (MERCH, _('Merchandasing')),
        (ADHESION, ('Adhésion')),
    ]

    categorie_article = models.CharField(max_length=3, choices=TYPE_CHOICES, default=BILLET,
                                         verbose_name=_("Type d'article"))

    id_product_stripe = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def get_id_product_stripe(self):
        configuration = Configuration.get_solo()
        if configuration.stripe_api_key and not self.id_product_stripe:
            if configuration.stripe_mode_test:
                stripe.api_key = configuration.stripe_test_api_key
            else:
                stripe.api_key = configuration.stripe_api_key

            if self.img:
                # noinspection PyUnresolvedReferences
                domain_url = connection.tenant.domains.all()[0].domain
                # noinspection PyUnresolvedReferences
                images = [f"https://{domain_url}{self.img.med.url}", ]
            else:
                images = []

            product = stripe.Product.create(
                name=f"{self.name}",
                images=images
            )
            self.id_product_stripe = product.id
            self.save()

            return self.id_product_stripe

        elif self.id_product_stripe:
            return self.id_product_stripe
        else:
            return False

    def reset_id_stripe(self):
        self.id_product_stripe = None
        self.save()


class Price(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="prices")

    name = models.CharField(max_length=50)
    prix = models.FloatField()

    NA, DIX, VINGT = 'NA', 'DX', 'VG'
    TVA_CHOICES = [
        (NA, _('Non applicable')),
        (DIX, _("10 %")),
        (VINGT, _('20 %')),
    ]

    vat = models.CharField(max_length=2,
                           choices=TVA_CHOICES,
                           default=NA,
                           verbose_name=_("Taux TVA"),
                           )

    id_price_stripe = models.CharField(max_length=30, null=True, blank=True)

    stock = models.SmallIntegerField(blank=True, null=True)
    max_per_user = models.PositiveSmallIntegerField(default=10)

    def range_max(self):
        return range(self.max_per_user + 1)

    def __str__(self):
        return f"{self.product.name} {self.name}"

    def get_id_price_stripe(self):
        configuration = Configuration.get_solo()
        if configuration.stripe_api_key and not self.id_price_stripe:
            if configuration.stripe_mode_test:
                stripe.api_key = configuration.stripe_test_api_key
            else:
                stripe.api_key = configuration.stripe_api_key

            price = stripe.Price.create(
                unit_amount=int("{0:.2f}".format(self.prix).replace('.', '')),
                currency="eur",
                product=self.product.get_id_product_stripe(),
                nickname=self.name,
            )

            self.id_price_stripe = price.id
            self.save()
            return self.id_price_stripe

        elif self.id_price_stripe:
            return self.id_price_stripe
        else:
            return False

    def reset_id_stripe(self):
        self.id_price_stripe = None
        self.save()


class Event(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)

    name = models.CharField(max_length=200)
    datetime = models.DateTimeField()

    short_description = models.CharField(max_length=250)
    long_description = models.TextField(blank=True, null=True)

    products = models.ManyToManyField(Product, blank=True)

    img = StdImageField(upload_to='images/',
                        validators=[MaxSizeValidator(1920, 1920)],
                        variations={
                            'fhd': (1920, 1920),
                            'hdr': (1280, 1280),
                            'crop': (510, 310, True),
                        },
                        delete_orphans=True
                        )

    reservations = models.PositiveSmallIntegerField(default=0)

    CONCERT = "LIV"
    FESTIVAL = "FES"
    REUNION = "REU"
    CONFERENCE = "CON"
    TYPE_CHOICES = [
        (CONCERT, _('Concert')),
        (FESTIVAL, _('Festival')),
        (REUNION, _('Réunion')),
        (CONFERENCE, _('Conférence')),
    ]

    categorie = models.CharField(max_length=3, choices=TYPE_CHOICES, default=CONCERT,
                                 verbose_name=_("Catégorie d'évènement"))

    def complet(self):
        # TODO: Benchmarker et tester si c'est pas mieux dans template
        if self.reservations >= Configuration.get_solo().jauge_max:
            return True
        else:
            return False

    def __str__(self):
        return f"{self.datetime.strftime('%d/%m')} {self.name}"

    class Meta:
        ordering = ('datetime',)
        verbose_name = _('Evenement')
        verbose_name_plural = _('Evenements')


class Reservation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    datetime = models.DateTimeField(auto_now=True)

    user_commande = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    event = models.ForeignKey(Event,
                              on_delete=models.PROTECT,
                              related_name="reservation")

    CANCELED, CREATED, UNPAID, PAID, PAID_ERROR, VALID, = 'C', 'R', 'U', 'P', 'PE', 'V'
    TYPE_CHOICES = [
        (CANCELED, _('Annulée')),
        (CREATED, _('Crée')),
        (UNPAID, _('Non payée')),
        (PAID, _('Payée')),
        (PAID_ERROR, _('Payée mais mail non valide')),
        (VALID, _('Validée')),
    ]

    status = models.CharField(max_length=3, choices=TYPE_CHOICES, default=CREATED,
                              verbose_name=_("Status de la réservation"))

    mail_send = models.BooleanField(default=False)
    mail_error = models.BooleanField(default=False)
    # paiement = models.OneToOneField(Paiement_stripe, on_delete=models.PROTECT, blank=True, null=True,
    #                                 related_name='reservation')

    options = models.ManyToManyField(OptionGenerale, blank=True)

    class Meta:
        ordering = ('-datetime',)

    def user_mail(self):
        return self.user_commande.email

    def paiements_paid(self):
        return self.paiements.filter(
            Q(status=Paiement_stripe.PAID) | Q(status=Paiement_stripe.VALID)
        )

    def articles_paid(self):
        articles_paid = []
        for paiement in self.paiements.all():
            for ligne in paiement.lignearticle_set.filter(
                    Q(status=LigneArticle.PAID) | Q(status=LigneArticle.VALID)
            ):
                articles_paid.append(ligne)
        return articles_paid

    def total_paid(self):
        total_paid = 0
        for article in self.articles_paid():
            article: LigneArticle
            total_paid += article.price.prix * article.qty
        return total_paid

    def __str__(self):
        return f"{str(self.uuid).partition('-')[0]} - {self.user_commande.email}"

    # def total_billet(self):
    #     total = 0
    #     for ligne in self.paiements.all():
    #         if ligne.billet:
    #             total += ligne.qty
    #     return total
    #
    # def total_prix(self):
    #     total = 0
    #     for ligne in self.paiements.all():
    #         if ligne.product:
    #             total += ligne.qty * ligne.product.prix
    #
    #     return total
    #
    # def _options_(self):
    #     return " - ".join([f"{option.name}" for option in self.options.all()])
    #


class Ticket(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="tickets")

    CREATED, NOT_ACTIV, NOT_SCANNED, SCANNED = 'C', 'N', 'K', 'S'
    SCAN_CHOICES = [
        (CREATED, _('Crée')),
        (NOT_ACTIV, _('Non actif')),
        (NOT_SCANNED, _('Non scanné')),
        (SCANNED, _('scanné')),
    ]

    status = models.CharField(max_length=1, choices=SCAN_CHOICES, default=CREATED,
                              verbose_name=_("Status du scan"))

    seat = models.CharField(max_length=20, default=_('Placement libre'))

    def pdf_filename(self):
        config = Configuration.get_solo()
        return f"{config.organisation.upper()} " \
               f"{self.reservation.event.datetime.astimezone().strftime('%d/%m/%Y')} " \
               f"{self.first_name.upper()} " \
               f"{self.last_name.capitalize()}" \
               f".pdf"


    def pdf_url(self):
        domain = connection.tenant.domains.all().first().domain
        api_pdf = reverse("ticket_uuid_to_pdf", args=[f"{self.uuid}"])
        protocol = "https://"
        port = ""
        if settings.DEBUG:
            protocol = "http://"
            port = ":8002"
        return f"{protocol}{domain}{port}{api_pdf}"


    def event(self):
        return self.reservation.event

    event.allow_tags = True
    event.short_description = 'Évènement'
    event.admin_order_field = 'reservation__event'

    def datetime(self):
        return self.reservation.datetime

    datetime.allow_tags = True
    datetime.short_description = 'Date de reservation'
    datetime.admin_order_field = 'reservation__datetime'

    def numero_uuid(self):
        return f"{self.uuid}".split('-')[0]

    class meta:
        ordering = ('-datetime',)


class Paiement_stripe(models.Model):
    """
    La commande
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    detail = models.CharField(max_length=50, blank=True, null=True)

    id_stripe = models.CharField(max_length=80, blank=True, null=True)
    metadata_stripe = JSONField(blank=True, null=True)

    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    last_action = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True)

    NON, OPEN, PENDING, EXPIRE, PAID, VALID, CANCELED = 'N', 'O', 'W', 'E', 'P', 'V', 'C'
    STATUT_CHOICES = (
        (NON, 'Lien de paiement non créé'),
        (OPEN, 'Envoyée a Stripe'),
        (PENDING, 'En attente de paiement'),
        (EXPIRE, 'Expiré'),
        (PAID, 'Payée'),
        (VALID, 'Payée et validée'),  # envoyé sur serveur cashless
        (CANCELED, 'Annulée'),
    )
    status = models.CharField(max_length=1, choices=STATUT_CHOICES, default=NON, verbose_name="Statut de la commande")

    traitement_en_cours = models.BooleanField(default=False)

    reservation = models.ForeignKey(Reservation, on_delete=models.PROTECT, blank=True, null=True,
                                    related_name="paiements")


    QRCODE, API_BILLETTERIE = 'Q', 'B'
    SOURCE_CHOICES = (
        (QRCODE, _('Depuis scan QR-Code')),
        (API_BILLETTERIE, _('Depuis billetterie')),
    )
    source = models.CharField(max_length=1, choices=SOURCE_CHOICES, default=API_BILLETTERIE,
                              verbose_name="Source de la commande")

    total = models.FloatField(default=0)

    def uuid_8(self):
        return f"{self.uuid}".partition('-')[0]

    def __str__(self):
        return self.uuid_8()

    def articles(self):
        return " - ".join(
            [f"{ligne.product.name} {ligne.qty * ligne.product.prix}€" for ligne in self.lignearticle_set.all()])


class LigneArticle(models.Model):
    uuid = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4)
    datetime = models.DateTimeField(auto_now=True)

    price = models.ForeignKey(Price, on_delete=models.CASCADE)

    qty = models.SmallIntegerField()

    carte = models.ForeignKey(CarteCashless, on_delete=models.PROTECT, blank=True, null=True)

    paiement_stripe = models.ForeignKey(Paiement_stripe, on_delete=models.PROTECT, blank=True, null=True)

    CANCELED, CREATED, UNPAID, PAID, VALID, = 'C', 'O', 'U', 'P', 'V'
    TYPE_CHOICES = [
        (CANCELED, _('Annulée')),
        (CREATED, _('Non envoyé en paiement')),
        (UNPAID, _('Non payée')),
        (PAID, _('Payée')),
        (VALID, _('Validée par serveur cashless')),
    ]

    status = models.CharField(max_length=3, choices=TYPE_CHOICES, default=CREATED,
                              verbose_name=_("Status de ligne article"))

    class Meta:
        ordering = ('-datetime',)

    def status_stripe(self):
        if self.paiement_stripe:
            return self.paiement_stripe.status
        else:
            return _('no stripe send')
