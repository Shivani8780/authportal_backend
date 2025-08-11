from authportal_backend.core.models import EBooklet
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authportal_backend.settings')
django.setup()


def populate_filenames():
    for ebooklet in EBooklet.objects.all():
        if not ebooklet.static_pdf_filename:
            ebooklet.static_pdf_filename = f"{ebooklet.name}.pdf"
            ebooklet.save()
            print(
                f"Updated {ebooklet.name} with static_pdf_filename: {ebooklet.static_pdf_filename}")


if __name__ == "__main__":
    populate_filenames()
