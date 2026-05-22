import unittest
from unittest.mock import patch, mock_open
import os
import json
import tempfile
import hashlib
import requests
import pyjoin

class TestPyJoinDevicesCache(unittest.TestCase):

    def setUp(self):
        self.api_key = "test_api_key_123"
        self.hashed_key = hashlib.sha256(self.api_key.encode('utf-8')).hexdigest()
        
        # Determine the cache path that would be resolved by _get_cache_path
        self.cache_path = pyjoin._get_cache_path(self.api_key)
        self.cache_dir = os.path.dirname(self.cache_path) if self.cache_path else None
        
        # Clean up cache files before each test
        if os.path.exists(self.cache_path):
            try:
                os.remove(self.cache_path)
            except Exception:
                pass

    def tearDown(self):
        # Clean up cache files after each test
        if os.path.exists(self.cache_path):
            try:
                os.remove(self.cache_path)
            except Exception:
                pass

    @patch('requests.get')
    def test_get_devices_success_online(self, mock_get):
        """Test that get_devices retrieves from API and saves to cache when successful."""
        mock_response = {
            "success": True,
            "records": [
                {"deviceName": "My Phone", "deviceId": "phone123"},
                {"deviceName": "My Tablet", "deviceId": "tablet456"}
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Execute
        devices = pyjoin.get_devices(self.api_key)

        # Assert correct devices returned
        expected_devices = [("My Phone", "phone123"), ("My Tablet", "tablet456")]
        self.assertEqual(devices, expected_devices)

        # Assert cache was written and is readable
        self.assertTrue(os.path.exists(self.cache_path))
        with open(self.cache_path, "r") as f:
            cached_data = json.load(f)
            # JSON serialization converts tuples to lists, so compare with lists
            self.assertEqual(cached_data, [["My Phone", "phone123"], ["My Tablet", "tablet456"]])

    @patch('requests.get')
    @patch('pyjoin.client._LOGGER')
    def test_get_devices_offline_fallback(self, mock_logger, mock_get):
        """Test that get_devices falls back to the cache when the network is down."""
        # 1. Populate the cache manually first
        os.makedirs(self.cache_dir, exist_ok=True)
        cached_devices = [["My Phone", "phone123"]]
        with open(self.cache_path, "w") as f:
            json.dump(cached_devices, f)

        # 2. Simulate connection failure
        mock_get.side_effect = requests.exceptions.ConnectionError("Offline")

        # Execute
        devices = pyjoin.get_devices(self.api_key)

        # Assert devices were retrieved from the cache (converted back to tuples or lists depending on load)
        # Since json.load returns lists inside lists:
        self.assertEqual(devices, [["My Phone", "phone123"]])

        # Assert that the warning log was called
        mock_logger.warning.assert_called()

    @patch('requests.get')
    @patch('pyjoin.client._LOGGER')
    def test_get_devices_offline_no_cache(self, mock_logger, mock_get):
        """Test that get_devices returns False and logs a critical error when offline and no cache is found."""
        # Ensure no cache exists
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)

        # Simulate network failure
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        # Execute
        devices = pyjoin.get_devices(self.api_key)

        # Assert it returns False
        self.assertFalse(devices)

        # Assert that the critical log was called
        mock_logger.critical.assert_called_with("Join API call failed and no offline cache is available.")

    @patch('requests.get')
    @patch('pyjoin.client._LOGGER')
    def test_get_devices_auth_error_fallback(self, mock_logger, mock_get):
        """Test that get_devices logs an error and falls back to cache on API Auth Error."""
        # 1. Populate the cache manually
        os.makedirs(self.cache_dir, exist_ok=True)
        cached_devices = [["My Phone", "phone123"]]
        with open(self.cache_path, "w") as f:
            json.dump(cached_devices, f)

        # 2. Mock API Auth Error
        mock_response = {
            "success": False,
            "userAuthError": True
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Execute
        devices = pyjoin.get_devices(self.api_key)

        # Assert it still returns cached data
        self.assertEqual(devices, [["My Phone", "phone123"]])

        # Assert error log was called
        mock_logger.error.assert_called()

class TestPyJoinUrlEncoding(unittest.TestCase):

    def setUp(self):
        self.api_key = "test_api_key_123"

    @patch('requests.get')
    def test_send_notification_encoding(self, mock_get):
        """Test send_notification encodes spaces and special characters."""
        pyjoin.send_notification(
            api_key=self.api_key,
            text="Hello & welcome!",
            device_id="phone 123",
            title="Notification Title / Subtitle"
        )
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn("text=Hello+%26+welcome!", called_url)
        self.assertIn("deviceId=phone+123", called_url)
        self.assertIn("title=Notification+Title+/+Subtitle", called_url)

    @patch('requests.get')
    def test_ring_device_encoding(self, mock_get):
        pyjoin.ring_device(
            api_key=self.api_key,
            device_id="phone 123"
        )
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn("find=true", called_url)
        self.assertIn("deviceId=phone+123", called_url)

    @patch('requests.get')
    def test_send_url_encoding(self, mock_get):
        pyjoin.send_url(
            api_key=self.api_key,
            url="https://example.com/some path?a=1&b=2",
            device_id="phone 123",
            title="My Cool Site & More"
        )
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn("url=https://example.com/some+path?a%3D1%26b%3D2", called_url)
        self.assertIn("title=My+Cool+Site+%26+More", called_url)
        self.assertIn("deviceId=phone+123", called_url)

    @patch('requests.get')
    def test_set_wallpaper_encoding(self, mock_get):
        pyjoin.set_wallpaper(
            api_key=self.api_key,
            url="https://example.com/wall paper.png",
            device_id="phone 123"
        )
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn("wallpaper=https://example.com/wall+paper.png", called_url)
        self.assertIn("deviceId=phone+123", called_url)

    @patch('requests.get')
    def test_send_file_encoding(self, mock_get):
        pyjoin.send_file(
            api_key=self.api_key,
            url="https://example.com/my file.pdf",
            device_id="phone 123",
            title="File & Attachment"
        )
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn("file=https://example.com/my+file.pdf", called_url)
        self.assertIn("title=File+%26+Attachment", called_url)
        self.assertIn("deviceId=phone+123", called_url)

    @patch('requests.get')
    def test_send_sms_encoding(self, mock_get):
        pyjoin.send_sms(
            api_key=self.api_key,
            sms_number="+1 234 567 890",
            sms_text="Hello world! & more text",
            device_id="phone 123"
        )
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn("smsnumber=%2B1+234+567+890", called_url)
        self.assertIn("smstext=Hello+world!+%26+more+text", called_url)
        self.assertIn("deviceId=phone+123", called_url)

    @patch('requests.get')
    def test_set_mediavolume_encoding(self, mock_get):
        pyjoin.set_mediavolume(
            api_key=self.api_key,
            mediavolume="50 percent",
            device_id="phone 123"
        )
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn("mediaVolume=50+percent", called_url)
        self.assertIn("deviceId=phone+123", called_url)

if __name__ == '__main__':
    unittest.main()

