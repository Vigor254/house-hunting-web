from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


ROOM_TYPE_CHOICES = [
    ("single", "Single room"),
    ("bedsitter", "Bedsitter"),
    ("1br", "1 Bedroom"),
    ("2br", "2 Bedroom"),
    ("hostel", "Hostel"),
    ("guesthouse", "Guest house"),
]

# Room types that use the "student pays a finder's fee once they commit" model.
FINDER_FEE_TYPES = ["single", "bedsitter", "1br", "2br"]
# Room types that use the "owner pays a monthly subscription to be listed" model.
SUBSCRIPTION_TYPES = ["hostel", "guesthouse"]

INQUIRY_STATUS_CHOICES = [
    ("new", "New"),
    ("in_discussion", "In discussion"),
    ("committed", "Committed"),
    ("closed", "Closed"),
]


class Landlord(models.Model):
    """A person or hostel/guest-house owner who lists a property."""
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    is_subscribed = models.BooleanField(
        default=False,
        help_text="For hostel/guest house owners: whether their monthly listing subscription is active.",
    )
    subscription_expires_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    """Deliberately lightweight — just enough to power alerts and matching."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    phone_number = models.CharField(max_length=20)
    is_tum_student = models.BooleanField(
        default=True,
        help_text="Whether this person is a Technical University of Mombasa student ('comrade'). "
                   "Controls whether distance-from-campus is shown, vs distance from their own location.",
    )
    preferred_room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, blank=True)
    budget_max = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({'TUM student' if self.is_tum_student else 'general user'})"


class Property(models.Model):
    """A single listing: a room, bedsitter, unit, hostel, or guest house."""
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name="properties")
    title = models.CharField(max_length=150)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    description = models.TextField(
        help_text="What the room/hostel offers: amenities, what's included, distance to campus, "
                   "water/electricity reliability, security, meals (for hostels/guest houses), etc.",
    )
    price_per_month = models.PositiveIntegerField()
    location_name = models.CharField(max_length=150, help_text="Area name, e.g. 'Tudor, near Tom Mboya stage'")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    distance_from_campus_km = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Straight-line or walking distance from Technical University of Mombasa, in km.",
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Only approved listings show on the public site. John approves manually before publishing.",
    )
    is_active = models.BooleanField(default=True, help_text="Still available / not yet rented out.")
    added_by_john = models.BooleanField(
        default=False, help_text="True if John personally scouted and added this listing rather than the landlord."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def uses_finder_fee(self):
        return self.room_type in FINDER_FEE_TYPES

    @property
    def uses_subscription(self):
        return self.room_type in SUBSCRIPTION_TYPES

    def __str__(self):
        return f"{self.title} ({self.get_room_type_display()})"


class PropertyPhoto(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="property_photos/")
    caption = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.property.title}"


class Inquiry(models.Model):
    """A student expressing interest in a property. John is the middleman for every message."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="inquiries")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="inquiries")
    status = models.CharField(max_length=20, choices=INQUIRY_STATUS_CHOICES, default="new")
    finder_fee_amount = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Set once status becomes 'committed' — typically about a third of one month's rent.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    committed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} -> {self.property} [{self.status}]"


class Message(models.Model):
    """A single message within an inquiry's conversation thread (student <-> John)."""
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name="messages")
    sender_is_student = models.BooleanField(default=True)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        return f"Message on inquiry #{self.inquiry_id} at {self.sent_at:%Y-%m-%d %H:%M}"


class Favorite(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="favorites")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "property")


class SavedSearch(models.Model):
    """Powers alerts: when a new property matches, the student gets notified via WhatsApp/SMS."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="saved_searches")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, blank=True)
    max_price = models.PositiveIntegerField(null=True, blank=True)
    keyword = models.CharField(max_length=100, blank=True, help_text="Free-text area match, e.g. 'Tudor'")
    created_at = models.DateTimeField(auto_now_add=True)

    def matches(self, property_obj):
        if self.room_type and property_obj.room_type != self.room_type:
            return False
        if self.max_price and property_obj.price_per_month > self.max_price:
            return False
        if self.keyword and self.keyword.lower() not in property_obj.location_name.lower():
            return False
        return True


class Review(models.Model):
    """Only meant to be created once an inquiry's status shows the student actually rented the place."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="reviews")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}/5 for {self.property}"
