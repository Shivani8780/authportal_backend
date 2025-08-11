from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    StaffUserListView,
    UserEBookletSelectionUpdateView,
    EBookletUploadView,
    UserEBookletView,
    ebooklet_pdf_view,
    ebooklet_static_pdf_view,
    ebooklet_page_images_view,
    ebooklets_list_view,
    registration_form_view,
    login_form_view,
    pdf_viewer_view,
)


from .user_ebooklets_views import user_ebooklets_view

urlpatterns = [
    # Viewer page route - Use custom template viewer
    path('ebooklet/<int:ebooklet_id>/view/',
         pdf_viewer_view, name='pdf-viewer'),

    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('staff/users/', StaffUserListView, name='staff-user-list'),
    path('user/ebooklet/', UserEBookletView, name='user-ebooklet'),
    path('user-ebooklets/', user_ebooklets_view, name='user-ebooklets'),
    path('staff/ebooklet/upload/',

         EBookletUploadView.as_view(), name='ebooklet-upload'),
    path('staff/ebooklet-selection/<int:pk>/',
         UserEBookletSelectionUpdateView.as_view(), name='ebooklet-selection-update'),
    # Direct PDF API endpoint for file serving
    path('ebooklet/<int:ebooklet_id>/pdf/',
         ebooklet_static_pdf_view, name='ebooklet-pdf-api'),
    path('ebooklet/<int:ebooklet_id>/page-images/',
         ebooklet_page_images_view, name='ebooklet-page-images'),

    path('ebooklets/', ebooklets_list_view, name='ebooklets-list'),
    path('registration-form/', registration_form_view, name='registration-form'),
    path('login-form/', login_form_view, name='login-form'),
]
