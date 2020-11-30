import unittest

from .gazette_access_tests import (
    GazetteAccessTest,
    GazetteTest,
    GazetteRequestTest,
    GazetteAccessInterfacesTest,
    GazetteAccessBaseTests,
)

from .api_tests import ApiGazettesEndpointTests

from .elasticsearch_tests import (
    ElasticSearchInterfaceTest,
    ElasticSearchDataMapperTest,
    ElasticSearchDataMapperPaginationTest,
    ElasticSearchDataMapperKeywordTest,
)

from .config_tests import BasicConfigurationTests
