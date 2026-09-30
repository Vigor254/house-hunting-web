from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import Property, Inquiry, Message, Favorite, SavedSearch, StudentProfile
from .forms import InquiryMessageForm, SavedSearchForm
from .integrations import notify_john_of_inquiry


def home(request):
    """Landing page: map + listing cards, with type/price/keyword filters."""
    properties = Property.objects.filter(is_approved=True, is_active=True)

    room_type = request.GET.get("room_type")
    max_price = request.GET.get("max_price")
    keyword = request.GET.get("keyword")

    if room_type:
        properties = properties.filter(room_type=room_type)
    if max_price:
        properties = properties.filter(price_per_month__lte=max_price)
    if keyword:
        properties = properties.filter(location_name__icontains=keyword)

    is_tum_student = True
    if request.user.is_authenticated and hasattr(request.user, "student_profile"):
        is_tum_student = request.user.student_profile.is_tum_student

    if is_tum_student:
        properties = properties.order_by("distance_from_campus_km")

    context = {
        "properties": properties,
        "is_tum_student": is_tum_student,
    }
    return render(request, "listings/home.html", context)


def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk, is_approved=True)
    return render(request, "listings/property_detail.html", {"property": property_obj})


@login_required
def create_inquiry(request, pk):
    """Student expresses interest — this is the moment John gets notified, per his preference
    that he personally verifies and mediates every conversation before the landlord is looped in."""
    property_obj = get_object_or_404(Property, pk=pk, is_approved=True)
    student_profile, _ = StudentProfile.objects.get_or_create(
        user=request.user, defaults={"phone_number": ""}
    )

    inquiry, created = Inquiry.objects.get_or_create(
        student=student_profile, property=property_obj,
    )
    if created:
        notify_john_of_inquiry(inquiry)
        django_messages.success(
            request,
            "Your interest has been sent. Blueprint Housing will reach out on WhatsApp to verify "
            "details and arrange a viewing.",
        )
    return redirect("inquiry_thread", pk=inquiry.pk)


@login_required
def inquiry_thread(request, pk):
    """The in-app conversation thread between a student and John for one inquiry."""
    inquiry = get_object_or_404(Inquiry, pk=pk, student__user=request.user)

    if request.method == "POST":
        form = InquiryMessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                inquiry=inquiry,
                sender_is_student=True,
                body=form.cleaned_data["body"],
            )
            return redirect("inquiry_thread", pk=inquiry.pk)
    else:
        form = InquiryMessageForm()

    return render(request, "listings/inquiry_thread.html", {"inquiry": inquiry, "form": form})


@login_required
def toggle_favorite(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    student_profile, _ = StudentProfile.objects.get_or_create(
        user=request.user, defaults={"phone_number": ""}
    )
    favorite, created = Favorite.objects.get_or_create(student=student_profile, property=property_obj)
    if not created:
        favorite.delete()
    return redirect("property_detail", pk=pk)


@login_required
def saved_searches(request):
    student_profile, _ = StudentProfile.objects.get_or_create(
        user=request.user, defaults={"phone_number": ""}
    )
    if request.method == "POST":
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            saved_search = form.save(commit=False)
            saved_search.student = student_profile
            saved_search.save()
            return redirect("saved_searches")
    else:
        form = SavedSearchForm()

    existing = student_profile.saved_searches.all()
    return render(request, "listings/saved_searches.html", {"form": form, "existing": existing})


def about(request):
    return render(request, "listings/about.html")
