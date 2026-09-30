from django.contrib import admin
from .models import (
    Landlord, StudentProfile, Property, PropertyPhoto,
    Inquiry, Message, Favorite, SavedSearch, Review,
)


class PropertyPhotoInline(admin.TabularInline):
    model = PropertyPhoto
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "room_type", "price_per_month", "location_name",
                     "distance_from_campus_km", "is_approved", "is_active", "added_by_john")
    list_filter = ("room_type", "is_approved", "is_active", "added_by_john")
    search_fields = ("title", "location_name", "description")
    inlines = [PropertyPhotoInline]
    actions = ["approve_listings"]

    @admin.action(description="Approve selected listings (publish to the site)")
    def approve_listings(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "email", "is_subscribed", "subscription_expires_on")
    search_fields = ("name", "phone_number", "email")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "is_tum_student", "preferred_room_type", "budget_max")
    list_filter = ("is_tum_student", "preferred_room_type")


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sent_at",)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("student", "property", "status", "finder_fee_amount", "created_at", "committed_at")
    list_filter = ("status",)
    inlines = [MessageInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("student", "property", "created_at")


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ("student", "room_type", "max_price", "keyword")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("student", "property", "rating", "created_at")
    list_filter = ("rating",)
