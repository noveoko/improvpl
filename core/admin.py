from django.contrib import admin
from django.utils.html import format_html

from .models import Event, Poll, Registration, Subscriber, Vote


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ['created_at']
    fields = ['name', 'email', 'created_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'city', 'date', 'event_type_badge', 'skill_level',
        'registration_display', 'is_active',
    ]
    list_filter = ['city', 'event_type', 'skill_level', 'is_active', 'date']
    search_fields = ['title', 'city', 'venue', 'instructor']
    date_hierarchy = 'date'
    inlines = [RegistrationInline]
    readonly_fields = ['registration_count_display', 'created_at']

    fieldsets = (
        (None, {
            'fields': (
                'title', 'event_type', 'skill_level', 'is_active',
            ),
        }),
        ('When & Where', {
            'fields': ('city', 'venue', 'date', 'start_time'),
        }),
        ('Details', {
            'fields': ('description', 'instructor', 'capacity', 'registration_count_display'),
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Type')
    def event_type_badge(self, obj):
        color = '#7C3AED' if obj.is_workshop else '#10B981'
        label = obj.get_event_type_display()
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;">{}</span>',
            color, label,
        )

    @admin.display(description='Registrations')
    def registration_display(self, obj):
        if obj.is_jam:
            return '—'
        return f'{obj.registration_count}/{obj.capacity}'

    @admin.display(description='Registrations')
    def registration_count_display(self, obj):
        if obj.is_jam:
            return 'Drop-in (no registration)'
        return f'{obj.registration_count} / {obj.capacity}'


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'event', 'created_at']
    list_filter = ['event__city', 'event__event_type', 'created_at']
    search_fields = ['name', 'email', 'event__title']
    readonly_fields = ['created_at']


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'city_interest', 'created_at']
    search_fields = ['email', 'city_interest']
    readonly_fields = ['created_at']


class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ['email', 'created_at']
    can_delete = False


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = [
        'city', 'event_type', 'progress_display', 'days_remaining',
        'is_active', 'succeeded', 'proposed_by_email',
    ]
    list_filter = ['is_active', 'succeeded', 'event_type', 'city']
    search_fields = ['city', 'proposed_by_email', 'description']
    readonly_fields = ['vote_count', 'created_at', 'progress_display']
    inlines = [VoteInline]

    fieldsets = (
        (None, {
            'fields': ('city', 'event_type', 'description', 'proposed_by_email'),
        }),
        ('Status', {
            'fields': ('deadline', 'vote_count', 'progress_display', 'is_active', 'succeeded'),
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Progress')
    def progress_display(self, obj):
        threshold = obj.threshold
        pct = obj.progress_percent
        color = '#10B981' if obj.succeeded else '#7C3AED'
        return format_html(
            '<span style="color:{};">{}/{} ({}%)</span>',
            color, obj.vote_count, threshold, pct,
        )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['email', 'poll', 'created_at']
    list_filter = ['poll__city', 'created_at']
    search_fields = ['email', 'poll__city']
    readonly_fields = ['created_at']