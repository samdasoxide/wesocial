import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action


def create_action(user, verb, target=None):
    # check for any similar action made in the last minute
    print("***Entering create action")
    now = timezone.now()
    last_minute = now - datetime.timedelta(seconds=60)
    similar_actions = Action.objects.filter(user=user.id,
                                            verb=verb,
                                            created__gte=last_minute)
    print("similar actions{}".format(similar_actions))
    if target:
        print("***target found")
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(target_ct=target_ct,
                                                 target_id=target.id)

    print("***About to check similar actions")
    if not similar_actions:
        print("***no simlar actions found")
        # no existing actions found
        action = Action(user=user, verb=verb, target=target)
        action.save()
        return True

    return False
