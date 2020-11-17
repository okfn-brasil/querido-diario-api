import unittest

from .gazette_access_tests import (
    GazetteAccessTest,
    GazetteTest,
    GazetteRequestTest,
    GazetteAccessInterfacesTest,
)
from .api_tests import ApiGazettesEndpointTests

from .elasticsearch_tests import (
    ElasticSearchInterfaceTest,
    ElasticSearchDataMapperTest,
    ElasticSearchDataMapperPaginationTest,
    ElasticSearchDataMapperKeywordTest,
)
