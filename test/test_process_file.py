import unittest
from unittest.mock import patch, MagicMock
import os
from tsmith.process_file import call_openrouter_api

class TestCallOpenRouterAPI(unittest.TestCase):
    @patch('process_file.requests.post')
    def test_call_openrouter_api(self, mock_post):
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'Mocked response from API'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Define test inputs
        file_content = "Test file content"
        user_prompts = ["What triggered the collapse?"]
        model = "openai/gpt-3.5-turbo"
        cache = True

        # Call the function
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'mock_api_key'}):
            result = call_openrouter_api(file_content, user_prompts, model, cache)

        # Assert the result
        self.assertEqual(result, "Mocked response from API")

        # Assert the request was made correctly
        mock_post.assert_called_once_with(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer mock_api_key",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "Given the attached text below:"
                            },
                            {
                                "type": "text",
                                "text": "Test file content",
                                "cache_control": {
                                    "type": "ephemeral"
                                }
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What triggered the collapse?"
                            }
                        ]
                    }
                ]
            }
        )

if __name__ == '__main__':
    unittest.main()
