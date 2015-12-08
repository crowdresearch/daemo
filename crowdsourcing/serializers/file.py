from __future__ import division
from rest_framework import serializers
from crowdsourcing.models import BatchFile
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.utils import get_delimiter
import pandas as pd


class BatchFileSerializer(DynamicFieldsModelSerializer):
    size = serializers.SerializerMethodField()

    class Meta:
        model = BatchFile
        fields = ('id', 'file', 'number_of_rows', 'name', 'first_row', 'format', 'column_headers', 'url', 'size',)
        read_only_fields = ('number_of_rows', 'name', 'first_row', 'format', 'column_headers',)

    def create(self, **kwargs):
        uploaded_file = self.validated_data['file']
        batch_file = BatchFile(deleted=False, file=uploaded_file)
        delimiter = get_delimiter(uploaded_file.name)
        df = pd.DataFrame(pd.read_csv(uploaded_file, sep=delimiter))
        df = df.where((pd.notnull(df)), None)
        column_headers = list(df.columns.values)
        num_rows = len(df.index)
        first_row = dict(zip(column_headers, list(df.values[0])))
        batch_file.number_of_rows = num_rows
        batch_file.column_headers = column_headers
        batch_file.first_row = first_row
        batch_file.name = uploaded_file.name
        batch_file.save()
        return batch_file

    def get_size(self, obj):
        size_bytes = obj.file.size
        size = '1 KB'
        if 1024 <= size_bytes < 1048576:
            size = str(round(size_bytes / 1024, 2)) + ' KB'
        elif size_bytes >= 1048576:
            size = str(round(size_bytes / 1024 / 1024, 2)) + ' MB'
        return size
