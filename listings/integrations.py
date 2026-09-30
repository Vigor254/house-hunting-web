"""
Blueprint Housing — external API integrations.

Every function in this file is a placeholder. The rest of the app calls
these functions normally (e.g. notify_john_of_inquiry(...)) so that once
you add your own API keys, you only need to fill in the bodies here —
nothing else in the project needs to change.

Add your credentials to environment variables (see .env.example in the
project root) rather than pasting them directly into this file.
"""

import logging
import os

logger = logging.getLogger("listings.integrations")


# ---------------------------------------------------------------------------
# WhatsApp Cloud API
# Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
# Needed env vars: WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID
# ---------------------------------------------------------------------------

def send_whatsapp_message(to_phone_number: str, message: str) -> bool:
    """
    Send a WhatsApp message via the WhatsApp Cloud API.
    Currently a placeholder — logs the message instead of sending it.
    """
    token = os.environ.get("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

    if not token or not phone_number_id:
        logger.info("[WHATSAPP PLACEHOLDER] Would send to %s: %s", to_phone_number, message)
        return False

    # TODO once you have credentials, uncomment and adapt:
    #
    # import requests
    # url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    # headers = {"Authorization": f"Bearer {token}"}
    # payload = {
    #     "messaging_product": "whatsapp",
    #     "to": to_phone_number,
    #     "type": "text",
    #     "text": {"body": message},
    # }
    # response = requests.post(url, headers=headers, json=payload, timeout=10)
    # return response.status_code == 200

    return False


def notify_john_of_inquiry(inquiry) -> None:
    """Called whenever a student creates a new Inquiry, per John's request to be alerted instantly."""
    john_whatsapp = os.environ.get("OWNER_WHATSAPP_NUMBER", "0714958724")
    message = (
        f"New inquiry: {inquiry.student} is interested in "
        f"'{inquiry.property.title}' (KES {inquiry.property.price_per_month}/mo)."
    )
    send_whatsapp_message(john_whatsapp, message)


def notify_landlord_of_interest(inquiry) -> None:
    """Called once John has verified the inquiry and wants to loop in the landlord."""
    landlord = inquiry.property.landlord
    message = (
        f"A student has expressed interest in your listing '{inquiry.property.title}'. "
        f"Blueprint Housing will coordinate the viewing with you shortly."
    )
    send_whatsapp_message(landlord.phone_number, message)


# ---------------------------------------------------------------------------
# SMS (e.g. Africa's Talking) — fallback for alerts when WhatsApp isn't ideal
# Needed env vars: AFRICAS_TALKING_USERNAME, AFRICAS_TALKING_API_KEY
# ---------------------------------------------------------------------------

def send_sms(to_phone_number: str, message: str) -> bool:
    """Placeholder SMS sender. Logs instead of sending until credentials are added."""
    username = os.environ.get("AFRICAS_TALKING_USERNAME")
    api_key = os.environ.get("AFRICAS_TALKING_API_KEY")

    if not username or not api_key:
        logger.info("[SMS PLACEHOLDER] Would send to %s: %s", to_phone_number, message)
        return False

    # TODO once you have credentials, uncomment and adapt:
    #
    # import africastalking
    # africastalking.initialize(username, api_key)
    # sms = africastalking.SMS
    # response = sms.send(message, [to_phone_number])
    # return True

    return False


def alert_saved_searches_for_new_property(property_obj) -> None:
    """Called after a new Property is approved — checks SavedSearch records and notifies matches."""
    from .models import SavedSearch  # local import to avoid circulars

    for saved_search in SavedSearch.objects.select_related("student").all():
        if saved_search.matches(property_obj):
            message = (
                f"New listing near your budget: '{property_obj.title}' — "
                f"KES {property_obj.price_per_month}/mo in {property_obj.location_name}."
            )
            send_whatsapp_message(saved_search.student.phone_number, message)
            send_sms(saved_search.student.phone_number, message)


# ---------------------------------------------------------------------------
# M-Pesa Daraja API — for hostel/guest house owner subscriptions
# Docs: https://developer.safaricom.co.ke/
# Needed env vars: MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_SHORTCODE, MPESA_PASSKEY
# ---------------------------------------------------------------------------

def initiate_subscription_payment(landlord, amount: int) -> dict:
    """
    Placeholder for an M-Pesa STK push to collect a hostel/guest house owner's
    monthly listing subscription. Returns a dict describing what would happen.
    """
    consumer_key = os.environ.get("MPESA_CONSUMER_KEY")
    consumer_secret = os.environ.get("MPESA_CONSUMER_SECRET")

    if not consumer_key or not consumer_secret:
        logger.info(
            "[M-PESA PLACEHOLDER] Would initiate STK push of KES %s to %s",
            amount, landlord.phone_number,
        )
        return {"status": "not_configured", "landlord": landlord.name, "amount": amount}

    # TODO once you have credentials, implement the OAuth token request and
    # STK push request per the Daraja API docs, then update
    # landlord.is_subscribed / landlord.subscription_expires_on on success.

    return {"status": "not_configured", "landlord": landlord.name, "amount": amount}


# ---------------------------------------------------------------------------
# Mapping API (e.g. Google Maps) — pins, distance calculation, geocoding
# Needed env var: GOOGLE_MAPS_API_KEY
# ---------------------------------------------------------------------------

def geocode_location(address: str):
    """
    Placeholder for turning a text address into (latitude, longitude).
    Until configured, returns None so the admin can enter coordinates manually.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        logger.info("[MAPS PLACEHOLDER] Would geocode: %s", address)
        return None

    # TODO once you have a key, call the Google Geocoding API here and
    # return (lat, lng) parsed from the response.
    return None


def calculate_distance_km(lat1, lng1, lat2, lng2) -> float:
    """
    Straight-line (haversine) distance in km — works with no external API,
    so distance_from_campus_km can be computed automatically once a
    property has coordinates, even before the mapping API key is added.
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371.0
    lat1, lng1, lat2, lng2 = map(radians, [float(lat1), float(lng1), float(lat2), float(lng2)])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)


# Technical University of Mombasa's approximate coordinates — used as the
# fixed reference point for distance_from_campus_km calculations.
TUM_LATITUDE = -4.0586
TUM_LONGITUDE = 39.6636
