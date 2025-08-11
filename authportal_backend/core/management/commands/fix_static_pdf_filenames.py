import os
from django.core.management.base import BaseCommand
from django.conf import settings
from authportal_backend.core.models import EBooklet


class Command(BaseCommand):
    help = 'Update EBooklet static_pdf_filename fields to match files in static/pdfs.'

    def handle(self, *args, **options):
        pdf_dir = os.path.join(settings.BASE_DIR, 'static', 'pdfs')
        pdf_files = set(os.listdir(pdf_dir))
        updated = 0
        for ebooklet in EBooklet.objects.all():
            # Try to match by name (replace spaces with underscores, try both)
            possible_names = [
                f"{ebooklet.name}.pdf",
                f"{ebooklet.name.replace(' ', '_')}.pdf",
                f"{ebooklet.name.replace('_', ' ')}.pdf"
            ]
            match = next((f for f in possible_names if f in pdf_files), None)
            if match:
                if ebooklet.static_pdf_filename != match:
                    ebooklet.static_pdf_filename = match
                    ebooklet.save()
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Updated: {ebooklet.name} -> {match}"))
            else:
                self.stdout.write(self.style.WARNING(
                    f"No matching PDF for: {ebooklet.name}"))
        self.stdout.write(self.style.SUCCESS(
            f"Done. Updated {updated} ebooklets."))
