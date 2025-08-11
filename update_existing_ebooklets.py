from authportal_backend.core.models import EBooklet
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authportal_backend.settings')
django.setup()


def update_ebooklets():
    for ebooklet in EBooklet.objects.all():
        ebooklet.save()
        print(f"Updated {ebooklet.name}")


if __name__ == "__main__":
    update_ebooklets()
