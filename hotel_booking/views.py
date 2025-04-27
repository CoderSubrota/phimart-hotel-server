from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'accounts':  request.build_absolute_uri('api/accounts/'),
        'hotels':    request.build_absolute_uri('api/hotels/'),
        'bookings':  request.build_absolute_uri('api/bookings/'),
        'dashboard': request.build_absolute_uri('api/dashboard/'),
    })


