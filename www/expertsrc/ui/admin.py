from ui.models import Domain, Level, UserProfile
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django import forms

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance.pk is None:
            self.empty_permitted = False

    class Meta:
        model = UserProfile

class UserProfileInline(admin.TabularInline):
    model = UserProfile
    form = UserProfileForm

class LevelInline(admin.TabularInline):
    model = Level
    extra = 3

class DomainAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Domain name:', {'fields': ['short_name']}),
        ('Description:', {'fields': ['description']}),
    ]
    inlines = [LevelInline]

class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline,]

admin.site.unregister(User)
admin.site.register(Domain, DomainAdmin)
admin.site.register(User, UserAdmin)
