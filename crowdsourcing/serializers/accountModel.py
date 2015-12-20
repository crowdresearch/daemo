from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.viewsets.google_drive import GoogleDriveUtil


class AccountModelSerializer(serializers.ModelSerializer):
    drive_contents = serializers.SerializerMethodField()

    class Meta:
        model = models.AccountModel
        read_only_fields = ('drive_contents')

    def get_drive_contents(self, request):
        drive_contents = []
        account_set = models.CredentialsModel.objects.filter(account=self.instance)
        for account_info in account_set:
            account = account_info.account
            if account.type == 'GOOGLEDRIVE':
                contents = GoogleDriveUtil.list_files_in_folder(request.folder_id, q=None)
                drive_contents.append([account.info, contents])
                # TODO: Handle 'account.type = DROPBOX' in the else case
        return drive_contents
