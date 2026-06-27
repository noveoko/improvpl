from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    city_interest = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class Event(models.Model):
    WORKSHOP = "workshop"
    JAM = "jam"
    EVENT_TYPE_CHOICES = [
        (WORKSHOP, "Workshop"),
        (JAM, "Jam"),
    ]

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ALL_LEVELS = "all_levels"
    SKILL_LEVEL_CHOICES = [
        (BEGINNER, "Beginner"),
        (INTERMEDIATE, "Intermediate"),
        (ALL_LEVELS, "All levels"),
    ]

    title = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    venue = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default=WORKSHOP)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default=ALL_LEVELS)
    capacity = models.PositiveIntegerField(default=20)
    description = models.TextField()
    headline_image = models.ImageField(
        upload_to="events/headlines/",
        blank=True,
        help_text="Optional promotional banner (recommended 16:9).",
    )
    description_image = models.ImageField(
        upload_to="events/descriptions/",
        blank=True,
        help_text="Optional photo shown with the event description.",
    )
    instructor = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.title} — {self.city} ({self.date})"

    @property
    def is_workshop(self):
        return self.event_type == self.WORKSHOP

    @property
    def is_jam(self):
        return self.event_type == self.JAM

    @property
    def registration_count(self):
        return self.registrations.count()

    @property
    def spots_remaining(self):
        return max(0, self.capacity - self.registration_count)

    @property
    def is_full(self):
        return self.is_workshop and self.registration_count >= self.capacity


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["event", "email"]]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.event}"


class Poll(models.Model):
    WORKSHOP = "workshop"
    JAM = "jam"
    EVENT_TYPE_CHOICES = [
        (WORKSHOP, "Workshop"),
        (JAM, "Jam"),
    ]

    city = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default=WORKSHOP)
    description = models.TextField()
    proposed_by_email = models.EmailField()
    deadline = models.DateField(blank=True)
    vote_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    succeeded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-vote_count", "-created_at"]

    def __str__(self):
        return f"{self.city} ({self.event_type}) — {self.vote_count} votes"

    def save(self, *args, **kwargs):
        if not self.deadline:
            days = getattr(settings, "POLL_DEADLINE_DAYS", 365)
            self.deadline = (timezone.now() + timedelta(days=days)).date()
        super().save(*args, **kwargs)

    @property
    def threshold(self):
        return getattr(settings, "POLL_VOTE_THRESHOLD", 100)

    @property
    def progress_percent(self):
        return min(100, int((self.vote_count / self.threshold) * 100))

    @property
    def days_remaining(self):
        delta = (self.deadline - timezone.now().date()).days
        return max(0, delta)

    @property
    def has_reached_threshold(self):
        return self.vote_count >= self.threshold

    def reconcile_vote_count(self):
        actual = self.votes.count()
        if self.vote_count != actual:
            self.vote_count = actual
            self.save(update_fields=["vote_count"])
        return actual


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["poll", "email"]]

    def __str__(self):
        return f"{self.email} — {self.poll.city}"


class HomePageContent(models.Model):
    hero_image = models.ImageField(
        upload_to="homepage/",
        blank=True,
        help_text="Optional full-width image above the homepage headline.",
    )

    class Meta:
        verbose_name = "Home page content"
        verbose_name_plural = "Home page content"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Home page content"
