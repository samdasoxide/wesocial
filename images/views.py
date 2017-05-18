import redis
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, \
                                  PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from actions.utils import create_action
from common.decorators import ajax_required
from .forms import ImageCreateForm
from .models import Image


@login_required
def image_create(request):
    if request.method == 'POST':
        # form is sent
        form = ImageCreateForm(data=request.POST)

        if form.is_valid():
            # form data is valid
            new_item = form.save(commit=False)
            # assign current user to the item
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')
            # redirect to new created item detail view
            return redirect(new_item.get_absolute_url())
    else:
        # Build form with data provided by wesocial via GET
        form = ImageCreateForm(data=request.GET)
        print(request.GET)

    return render(request, 'images/image/create.html', {'section': 'images',
                                                        'form': form})


# connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # increment total views by 1
    total_views = r.incr('image:{}:views'.format(image.id))
    # increment ranking by 1
    r.zincrby('image_ranking', image.id, 1)

    return render(request,
                  'images/image/detail.html',
                  {'section': 'images',
                   'image': image,
                   'total_views': total_views})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
                create_action(request.user, 'unliked', image)
            return JsonResponse({'status': 'ok'})
        except:
            pass
        return JsonResponse({'status': 'ko'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 2)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # if the request is AJAX and the page is out of range
            # return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'images/image/list_ajax.html',
                      {'section': 'images', 'images': images})
    return render(request,
                  'images/image/list.html',
                  {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    # get image ranking dictionary
    image_ranking = r.zrange('image_ranking', 0, -1,
                             desc=True)[:10]
    print("image-ranking{}".format(image_ranking))
    image_ranking_ids = [int(id) for id in image_ranking]
    # get most viewd images
    print('rank-ids{}'.format(image_ranking_ids))
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    print("most_viewed1{}".format(most_viewed))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    print("most_viewed2{}".format(most_viewed))
    return render(request,
                  'images/image/ranking.html',
                  {'section': 'images',
                   'most_viewed': most_viewed})
