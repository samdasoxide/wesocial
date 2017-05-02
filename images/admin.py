from django.contrib import admin
from .models import Image


class ImageAdmin(admin.ModelAdmin):
    '''
        Admin View for Image
    '''
    list_display = ('title', 'slug', 'image', 'created')
    list_filter = ('created',)


admin.site.register(Image, ImageAdmin)
