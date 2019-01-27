from rest_framework.filters import SearchFilter
from django.db import models


@models.Field.register_lookup
class Search(models.Lookup):
    lookup_name = 'isearch'

    def as_sql(self, compiler, connection):
        similarity__gt = 0.2
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'SIMILARITY(%s, %s)>%s' % (lhs, rhs, similarity__gt), params


class CommonSearchFilter(SearchFilter):
    def construct_search(self, field_name):
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('$'):
            return "%s__iregex" % field_name[1:]
        elif field_name.startswith('~'):
            return "%s__contains" % field_name[1:]
        else:
            return "%s__isearch" % field_name
