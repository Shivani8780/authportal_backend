from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import UserEBookletSelection, EBooklet

User = get_user_model()


@login_required
def dashboard_view(request):
    """
    Main dashboard view that redirects to userbooklet
    """
    return redirect('dashboard-home')


@login_required
def dashboard_home_view(request):
    """
    Dashboard home page showing user's ebooklets
    """
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

    context = {
        'ebooklets': ebooklets_data,
        'user': user
    }

    return render(request, 'dashboard.html', context)


@login_required
def dashboard_api_view(request):
    """
    API endpoint for dashboard data
    """
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
                'pdf_url': f"/api/ebooklet/{ebooklet.id}/pdf/",
                'static_pdf_url': f"/api/ebooklet/{ebooklet.id}/pdf/"
            })

    return JsonResponse({'ebooklets': ebooklets_data})
