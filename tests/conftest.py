import pytest
import sys
from unittest.mock import MagicMock

# Mock the Google Cloud libraries
MOCK_MODULES = [
    'google.cloud.resourcemanager_v3',
    'google.cloud.service_usage',
    'google.cloud.compute_v1',
    'google.cloud.storage',
    'google.cloud.billing.v1',
    'google.auth',
    'google.iam.v1',
    'google.auth.exceptions',
    'googleapiclient',
    'googleapiclient.discovery'
]

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

# Mock specific classes
sys.modules['google.cloud.resourcemanager_v3'].ProjectsClient = MagicMock
sys.modules['google.cloud.service_usage'].ServiceUsageClient = MagicMock
sys.modules['google.cloud.compute_v1'].InstancesClient = MagicMock
sys.modules['google.cloud.compute_v1'].ZonesClient = MagicMock
sys.modules['google.cloud.storage'].Client = MagicMock
sys.modules['google.cloud.billing.v1'].CloudBillingClient = MagicMock
sys.modules['google.cloud.billing.v1'].CloudCatalogClient = MagicMock
sys.modules['google.auth'].default = MagicMock
sys.modules['google.iam.v1'].iam_policy_pb2 = MagicMock
sys.modules['googleapiclient.discovery'].build = MagicMock 