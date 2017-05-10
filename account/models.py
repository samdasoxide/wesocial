from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%y/%m/%d',
                              blank=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)


class Contact(models.Model):
    user_from = models.ForeignKey(User,
                                  related_name='rel_from_set')
    user_to = models.ForeignKey(User,
                                related_name='rel_to_set')
    created = models.DateField(auto_now_add=True,
                               db_index=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)


# Add following field to User dynamically
# self: creates relationship to the same model
# through: tell django to use the intermediary model for the r/ship
# symmetrical false: if I follow you it doesn't mean you automatically follow me
User.add_to_class('following',
                  models.ManyToManyField('self',
                                         through=Contact,
                                         related_name='followers',
                                         symmetrical=False))
