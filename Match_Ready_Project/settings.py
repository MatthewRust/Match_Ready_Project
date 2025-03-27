# Match_Ready_Project/settings.py

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ... (Keep other settings like SECRET_KEY, DEBUG)

SECRET_KEY = '5hsrx#n+uk(4_vfvoz02v(tpk%0i3u@(!99e&f%+ae6a1dn4)m'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Add your development hosts here
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'), # Uses the BASE_DIR defined earlier
    }
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Match_Ready',
]

# Corrected TEMPLATE_DIR definition
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Needed for login sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <<< THIS ADDS request.user
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Match_Ready_Project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Corrected DIRS path
        'DIRS': [TEMPLATE_DIR,],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Ensure your custom context processor is here
                'Match_Ready.context_processors.user_role',
            ],
        },
    },
]

# ... (Keep WSGI_APPLICATION, DATABASES, AUTH_PASSWORD_VALIDATORS, PASSWORD_HASHERS)

# Internationalization
# ... (Keep LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_L10N, USE_TZ)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Correct path for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Login URL
LOGIN_URL = '/Match_Ready/login/'

# Default primary key field type (Optional but good practice for newer Django versions)
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'