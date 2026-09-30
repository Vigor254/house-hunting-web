# Blueprint Housing

"Find Your Next Home, Near Your School" — a student housing discovery platform
starting at Technical University of Mombasa (TUM).

This is a real, working Django project: models, admin, views, templates and
styling are all functional. The external APIs (WhatsApp, SMS, M-Pesa, Google
Maps) are wired in but **intentionally left as placeholders** — see
"Configuring the real APIs" below for exactly what to fill in and where.

## What's already working

- Django models: `Landlord`, `StudentProfile`, `Property`, `PropertyPhoto`,
  `Inquiry`, `Message`, `Favorite`, `SavedSearch`, `Review`
- Django admin — add/approve listings, manage inquiries, everything
- Public pages: home (map + filters + listing cards), property detail,
  about page, in-app inquiry thread, saved alerts
- Finder's fee logic for rooms/bedsitters vs. subscription logic for
  hostels/guest houses (see `Property.uses_finder_fee` / `uses_subscription`)
- Distance-from-campus calculation (haversine formula, no API key needed) —
  see `listings/integrations.py` → `calculate_distance_km`
- Sample data seeding command so you can see it running immediately

## Quick start

```bash
cd blueprint_housing_django
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt

python3 manage.py migrate
python3 manage.py createsuperuser   # create your own admin login
python3 manage.py seed_demo_data    # adds 6 sample listings so the site isn't empty
python3 manage.py runserver
```

Then visit:
- http://127.0.0.1:8000/ — the public site
- http://127.0.0.1:8000/admin/ — the admin, log in with the superuser you created
- http://127.0.0.1:8000/about/ — the about page

## Adding real listings

In the admin, add a `Landlord` first, then add a `Property` for them. Tick
**"is_approved"** for it to appear on the public site — this is the manual
approval step you asked for, so nothing goes live without your sign-off.

## Configuring the real APIs

Everything below lives in `listings/integrations.py`. Every function there
currently just logs what it *would* do — nothing is sent anywhere until you
add credentials. This keeps the rest of the app (views, templates) completely
unaffected when you're ready to go live with each one.

1. Copy `.env.example` to `.env` and fill in the keys as you get them.
2. Install `python-dotenv` (or use your hosting provider's environment
   variable settings) so those variables are actually loaded.
3. Fill in the `TODO` sections in `integrations.py` one at a time:
   - **WhatsApp Cloud API** — `send_whatsapp_message()`. This is what
     notifies you the instant a student inquires (`notify_john_of_inquiry`),
     and what you'd use to message landlords once you're ready to loop them
     in (`notify_landlord_of_interest`).
   - **SMS (Africa's Talking)** — `send_sms()`, used as a backup channel for
     alerts in `alert_saved_searches_for_new_property`.
   - **M-Pesa Daraja API** — `initiate_subscription_payment()`, for
     collecting the monthly subscription from hostel/guest house owners.
   - **Google Maps** — `geocode_location()`, for turning a typed address
     into coordinates automatically. Until this is added, just enter
     latitude/longitude manually in the admin (Google Maps app → long-press
     a location → copy coordinates).

You do **not** need any of these keys to run the site, add listings, or test
the inquiry flow locally — they only gate the "send this over WhatsApp/SMS/
M-Pesa" step.

## Deploying

This project runs anywhere Django does (Railway, PythonAnywhere, a VPS,
etc.). Before deploying:
- Set `DEBUG = False` in `blueprint_housing/settings.py`
- Set a real `SECRET_KEY` via environment variable
- Set `ALLOWED_HOSTS` to your real domain
- Switch `DATABASES` to Postgres if your host doesn't persist SQLite files
- Run `python3 manage.py collectstatic`

## Project structure

```
blueprint_housing_django/
├── blueprint_housing/       # project settings, root urls.py
├── listings/                 # the whole app
│   ├── models.py             # Property, Inquiry, StudentProfile, etc.
│   ├── views.py               # home, detail, inquiry thread, alerts
│   ├── forms.py
│   ├── admin.py
│   ├── integrations.py       # <-- WhatsApp / SMS / M-Pesa / Maps go here
│   └── management/commands/seed_demo_data.py
├── templates/listings/       # home, property_detail, about, etc.
├── static/                   # css/style.css, images/logo.png
├── requirements.txt
└── .env.example
```
