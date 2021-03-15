from rest_framework.generics import RetrieveAPIView

from ..services.reports import Report
from ..models import Room


class ReportView(RetrieveAPIView):
    queryset = Room.objects.all()

    def get(self, request, *args, **kwargs):
        connection_uuid = kwargs.get('uuid')
        token = kwargs.get('token')
        return Report.create_xlsx(connection_uuid, token)
