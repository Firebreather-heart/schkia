from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Parent
from results.models import Student, ClassRoom


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'signature')}),
        ('Personal info', {'fields': ('username', )}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ['email', 'username']
    ordering = ['email']

    verbose_name = 'User'


class ClassRoomNameFilter(admin.SimpleListFilter):
    title = 'Class'  
    parameter_name = 'class'  

    def lookups(self, request, model_admin):
        # Return the human-readable name for each choice
        return ClassRoom.NAME_CHOICES

    def queryset(self, request, queryset):
        # Filter by the database value of the choice
        if self.value():
            return queryset.filter(classroom__name=self.value())
        return queryset

class StudentAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'date_of_birth', 'hostel', 'gender',
                    'phone_number', 'roll_id', 'number', 'classroom', 'created_at')
    search_fields = ('fullname', 'phone_number',
                     'roll_id', 'number', 'classroom')
    list_filter = ('gender', ClassRoomNameFilter, 'created_at')
    ordering = ('fullname',)
    fieldsets = (
        (None, {
            'fields': ('fullname', 'date_of_birth', 'hostel', 'gender', 'phone_number', 'roll_id', 'number', 'classroom')
        }),
    )


class ParentAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phone_number', )
    search_fields = ('fullname', 'phone_number',  'students')
    ordering = ('fullname',)
    # fieldsets = (
    #     (None, {
    #         'fields': ('fullname', 'phone_number', )
    #     }),
    # )


admin.site.register(Parent, ParentAdmin)

admin.site.register(Student, StudentAdmin)


admin.site.register(CustomUser, CustomUserAdmin)
