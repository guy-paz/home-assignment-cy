import unittest

from fastapi.testclient import TestClient

from WordProcessor.app.main import app

client = TestClient(app)


# e2e test - sort of
class TestWordService(unittest.IsolatedAsyncioTestCase):
    async def test_add_words_basic_summary(self):
        expected = dict()
        expected2 = dict()

        # 1. checking response on empty db
        response = client.get("/words/",headers={"token":"cyolo"})
        assert response.status_code == 200
        expected["top5"] = None
        expected["least"] = 0
        expected["median"] = 0
        response_json = response.json()
        response_json.pop("request_id")
        assert response_json == expected

        # 2. adding words
        word_addition_response = client.post("/words/", json={"words":["a","a","plus","b","plus","not",
                                                                       "a","plus","a","plus","fffff","b"
                                                                        ,"b","a","not"]},
                                             headers={"token":"cyolo"})
        assert word_addition_response.status_code == 202

        # 3. verifying proper addition and summary
        summary_response = client.get("/words/", headers={"token":"cyolo"})
        assert summary_response.status_code == 200
        expected2["top5"] = {"a":5,"plus":4,"b":3,"not":2,"fffff":1}
        expected2["least"] = 1
        expected2["median"] = 3
        summary_response_json = summary_response.json()
        summary_response_json.pop("request_id")
        assert summary_response_json == expected2
