from django.core.management.base import BaseCommand
from authportal_backend.core.models import EBooklet


class Command(BaseCommand):
    help = 'Updates all existing ebooklets to populate the static_pdf_filename field.'

    def handle(self, *args, **options):
        for ebooklet in EBooklet.objects.all():
            ebooklet.save()
            self.stdout.write(self.style.SUCCESS(
                f'Successfully updated ebooklet "{ebooklet.name}"'))
