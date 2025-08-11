from django.views.decorators.http import require_GET
import logging
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .utils import generate_pdf_page_images
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.http import Http404
import mimetypes
import os
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, FileResponse
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import EBooklet, UserEBookletSelection
from .views_custom import log_request, log_error

import json

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(View):
    def post(self, request):
        log_request(request)
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            phone_number = data.get('phone_number')
            memberID = data.get('memberID')
            ebooklet_ids = data.get('ebooklets', [])

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required.'}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists.'}, status=400)

            user = User.objects.create_user(
                username=username, email=email, password=password)
            user.phone_number = phone_number
            user.memberID = memberID
            user.save()

            # Create UserEBookletSelection entries
            for ebooklet_id in ebooklet_ids:
                try:
                    ebooklet = EBooklet.objects.get(pk=ebooklet_id)
                    user_ebooklet_selection = UserEBookletSelection.objects.create(
                        user=user,
                        view_option='none'  # default or customize as needed
                    )
                    user_ebooklet_selection.ebooklet.set([ebooklet])
                except EBooklet.DoesNotExist:
                    continue

            return JsonResponse({'message': 'User registered successfully.'})
        except Exception as e:
            log_error(e)
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def post(self, request):
        log_request(request)
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return JsonResponse({'message': 'Login successful.', 'token': token.key})
            else:
                return JsonResponse({'error': 'Invalid credentials.'}, status=401)
        except Exception as e:
            log_error(e)
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def StaffUserListView(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this resource.")
    users = User.objects.all().values('id', 'username', 'email', 'is_staff')
    return JsonResponse(list(users), safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserEBookletSelectionUpdateView(View):
    def post(self, request, pk):
        # Implement update logic for UserEBookletSelection here
        return JsonResponse({'message': 'Update endpoint not implemented yet.'})


@method_decorator(csrf_exempt, name='dispatch')
class EBookletUploadView(View):
    def post(self, request):
        # Implement ebooklet upload logic here
        # For example, handle file upload and save to EBooklet model
        try:
            pdf_file = request.FILES.get('pdf_file')
            name = request.POST.get('name', 'Untitled')
            if not pdf_file:
                return JsonResponse({'error': 'No PDF file uploaded.'}, status=400)

            ebooklet = EBooklet.objects.create(name=name, pdf_file=pdf_file)
            ebooklet.save()

            # Generate page images for the uploaded PDF
            generate_pdf_page_images(ebooklet)

            return JsonResponse({'message': 'EBooklet uploaded and processed successfully.', 'ebooklet_id': ebooklet.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def UserEBookletView(request):

    user = request.user
    selections = UserEBookletSelection.objects.filter(
        user=user, approved=True).select_related('user').prefetch_related('ebooklet')
    ebooklets_data = []
    for selection in selections:
        for ebooklet in selection.ebooklet.all():
            ebooklets_data.append({
                'id': ebooklet.id,
                'name': ebooklet.name,
                'view_option': selection.view_option,
                'approved': selection.approved,
            })
    return JsonResponse({'ebooklets': ebooklets_data})


def ebooklets_list_view(request):
    # Return list of all ebooklets
    ebooklets = EBooklet.objects.all().values('id', 'name')
    return JsonResponse(list(ebooklets), safe=False)


def registration_form_view(request):
    """
    Serve the HTML registration form
    """
    return render(request, 'registration.html')


def login_form_view(request):
    """
    Serve the HTML login form
    """
    return render(request, 'login.html')


def home_view(request):
    """
    Serve the HTML home page
    """
    return render(request, 'registration.html')


@login_required
def pdf_viewer_view(request, ebooklet_id):
    """
    Serve the PDF viewer page with necessary context
    """
    try:
        ebooklet = get_object_or_404(EBooklet, pk=ebooklet_id)

        # Check if user has access to this ebooklet
        selections = UserEBookletSelection.objects.filter(
            user=request.user, ebooklet=ebooklet, approved=True)
        if not selections.exists():
            return HttpResponseForbidden("You do not have access to this ebooklet.")

        selection = selections.first()
        if selection.view_option != 'full':
            return HttpResponseForbidden("You do not have full access to view this ebooklet.")

        # Pass more context to the template
        context = {
            'ebooklet': ebooklet,
            'ebooklet_id': ebooklet_id,
            'ebooklet_name': ebooklet.name,
            'api_url': f'/api/ebooklet/{ebooklet_id}/view/',
            'view_option': selection.view_option,
            'pdf_filename': ebooklet.static_pdf_filename
        }
        response = render(request, 'pdf_viewer.html', context)
        # Allow iframe from same origin
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    except EBooklet.DoesNotExist:
        return JsonResponse({'error': 'EBooklet not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


@login_required
def ebooklet_pdf_view(request, ebooklet_id):
    user = request.user
    try:
        ebooklet = get_object_or_404(EBooklet, pk=ebooklet_id)

        # Check if user has approved selection for this ebooklet
        selections = UserEBookletSelection.objects.filter(
            user=user, ebooklet=ebooklet, approved=True)
        if not selections.exists():
            logger.error(
                f"User {user} does not have access to ebooklet {ebooklet_id}")
            return HttpResponseForbidden("You do not have access to this ebooklet.")

        # Check view_option for the selection
        selection = selections.first()
        if selection.view_option == 'none':
            logger.error(
                f"User {user} has no view access to ebooklet {ebooklet_id}")
            return HttpResponseForbidden("You do not have access to view this ebooklet.")
        elif selection.view_option == 'preview':
            # TODO: Implement preview logic, e.g., serve a preview PDF or partial content
            logger.error(
                f"Preview access not implemented for ebooklet {ebooklet_id}")
            return HttpResponseForbidden("Preview access not implemented yet.")
        elif selection.view_option == 'full':
            # Serve the full PDF file
            if not ebooklet.pdf_file:
                logger.error(f"EBooklet {ebooklet_id} has no PDF file.")
                return HttpResponseForbidden("PDF file not available.")
            try:
                file_path = ebooklet.pdf_file.path
                logger.debug(
                    f"Attempting to open PDF file at path: {file_path}")
                if not os.path.exists(file_path):

                    logger.error(
                        f"PDF file does not exist at path: {file_path}")
                    return JsonResponse({'error': 'PDF file not found on server.'}, status=404)
                # Additional debug info
                logger.debug(f"File size: {os.path.getsize(file_path)} bytes")
                content_type = 'application/pdf'
                response = FileResponse(
                    open(file_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{ebooklet.name}.pdf"'
                response['X-Frame-Options'] = 'SAMEORIGIN'
                response['Access-Control-Allow-Origin'] = '*'
                response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
                response['Access-Control-Allow-Credentials'] = 'true'
                return response
            except Exception as e:
                logger.error(
                    f"Error opening PDF file for ebooklet {ebooklet_id}: {e}", exc_info=True)
                return JsonResponse({'error': 'Error opening PDF file.'}, status=500)
        else:
            logger.error(
                f"Invalid access level {selection.view_option} for ebooklet {ebooklet_id}")
            return HttpResponseForbidden("Invalid access level.")
    except Exception as e:
        logger.error(f"Error serving ebooklet PDF: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error while fetching PDF.'}, status=500)


logger = logging.getLogger(__name__)


@login_required
@require_GET
def ebooklet_page_images_view(request, ebooklet_id):
    user = request.user
    try:
        ebooklet = get_object_or_404(EBooklet, pk=ebooklet_id)

        # Check if user has approved selection for this ebooklet
        selections = UserEBookletSelection.objects.filter(
            user=user, ebooklet=ebooklet, approved=True)
        if not selections.exists():
            return HttpResponseForbidden("You do not have access to this ebooklet.")

        # Check view_option for the selection
        selection = selections.first()
        if selection.view_option != 'full':
            return HttpResponseForbidden("You do not have full access to view this ebooklet.")

        # Construct URLs for pre-rendered page images
        media_url = settings.MEDIA_URL
        page_images_dir = os.path.join('ebooklet_pages', str(ebooklet.id))
        page_images_path = os.path.join(settings.MEDIA_ROOT, page_images_dir)

        import logging
        logger.debug(
            f"ebooklet_page_images_view: page_images_path={page_images_path}")
        if not os.path.exists(page_images_path):
            logger.error(
                f"Page images path does not exist: {page_images_path}")
            return JsonResponse({'error': 'Page images not found. Please upload and process the ebooklet again.'}, status=404)

        # List all page image files sorted by page number
        files = sorted(f for f in os.listdir(
            page_images_path) if f.endswith('.png'))
        logger.debug(f"Files found in page_images_path: {files}")
        page_urls = [request.build_absolute_uri(os.path.join(
            media_url, page_images_dir, f)) for f in files]

        return JsonResponse({'page_images': page_urls})
    except Exception as e:
        logger.error(f"Error serving ebooklet page images: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error while fetching page images.'}, status=500)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_GET
def ebooklet_static_pdf_view(request, ebooklet_id):
    """
    Serve static PDF files with authentication and access control.
    """
    user = request.user
    try:
        ebooklet = get_object_or_404(EBooklet, pk=ebooklet_id)

        # Check if user has approved selection for this ebooklet
        selections = UserEBookletSelection.objects.filter(
            user=user, ebooklet=ebooklet, approved=True)
        if not selections.exists():
            logger.error(
                f"User {user} does not have access to ebooklet {ebooklet_id}")
            return HttpResponseForbidden("You do not have access to this ebooklet.")

        selection = selections.first()
        if selection.view_option != 'full':
            logger.error(
                f"User {user} does not have full view access to ebooklet {ebooklet_id}")
            return HttpResponseForbidden("You do not have full access to view this ebooklet.")

        # Get the static filename from the model
        static_filename = getattr(ebooklet, 'static_pdf_filename', None)
        if not static_filename:
            logger.error(
                f"Static PDF filename not set for EBooklet {ebooklet_id}")
            return JsonResponse({'error': 'Static PDF not configured for this item.'}, status=404)

        # Construct the path to the static PDF file
        static_pdf_path = os.path.join(
            settings.STATICFILES_DIRS[0], 'pdfs', static_filename)

        if os.path.exists(static_pdf_path):
            logger.info(
                f"Serving static PDF for ebooklet {ebooklet_id} from {static_pdf_path}")
            response = FileResponse(
                open(static_pdf_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = 'inline'  # Force inline display
            # Allow iframe from same origin
            response['X-Frame-Options'] = 'SAMEORIGIN'
            # Allow embedding
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            logger.error(
                f"Static PDF file not found at path: {static_pdf_path}")
            return JsonResponse({'error': f"Static PDF file '{static_filename}' not found."}, status=404)

    except EBooklet.DoesNotExist:
        return JsonResponse({'error': 'EBooklet not found.'}, status=404)
    except Exception as e:
        logger.error(
            f"Error serving static PDF for ebooklet {ebooklet_id}: {e}", exc_info=True)
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
