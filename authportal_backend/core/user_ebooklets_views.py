from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserEBookletSelection


@login_required
def user_ebooklets_view(request):
    """
    Displays the user's approved ebooklets.
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

    return render(request, 'user_ebooklets.html', context)
