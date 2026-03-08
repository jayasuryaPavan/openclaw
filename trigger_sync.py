import os
import django
import sys

# Setup Django
sys.path.append(r"C:\Workspace\Classyy\Backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User
from apps.users.analytics_sync import sync_analytics_for_user

def main():
    try:
        user = User.objects.get(email='influencer@brandstudios.in')
        print(f"Syncing for: {user.email}")
        analytics = sync_analytics_for_user(user)
        print(f"IG Followers: {analytics.ig_followers}")
        print(f"YT Subscribers: {analytics.yt_subscribers}")
        print(f"Last Synced: {analytics.last_synced_at}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
