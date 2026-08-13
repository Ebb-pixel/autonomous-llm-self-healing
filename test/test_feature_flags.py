from unittest.mock import MagicMock, patch

from services.llm_service.feature_flags import FeatureFlagManager


def test_feature_flag_returns_true():
    with patch.dict("os.environ",{"LD_SDK_KEY":"test_key", "LD_ENVIRONMENT":"test"}):
        mock_client=MagicMock()
        mock_client.is_initialized.return__value=True
        mock_client.variation.return_value=True

        with patch("services.llm_service.feature_flags.ldclient.get", return_value=mock_client):
            manager=FeatureFlagManager()

            result=manager.is_enabled("enable-new-llm-agent")

    assert result is True
