__author__ = 'megha'

from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.viewsets.google_drive import GoogleDriveUtil

class AccountModelSerializer (serializers.ModelSerializer):
    drive_contents = serializers.SerializerMethodField()

    class Meta:
        model = models.AccountModel
        read_only_fields = ('drive_contents')

    def get_drive_contents(self, instance):
        drive_contents = []
        account_set = models.CredentialsModel.objects.filter(account = instance)
        for account_info in account_set:
            account = account_info.account
            credentials = account_info.credential
            if account.type == 'GOOGLEDRIVE':
                contents = GoogleDriveUtil.list_DriveContents(self, credentials)
                drive_contents.append([account.info, contents])
            #TODO: Handle 'account.type = DROPBOX' in the else case
        return drive_contents