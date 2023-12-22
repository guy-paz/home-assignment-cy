import uuid

import unittest
from datetime import datetime, timezone

from WordProcessor.app.objects import WordProcessorSummaryResponse
from WordProcessor.app.wordservice import WordService


class TestWordService(unittest.IsolatedAsyncioTestCase):

    async def test_word_service_with_no_words(self):
        request_id = str(uuid.uuid4())
        timestamp = str(datetime.now(timezone.utc))
        expected_empty_summary = WordProcessorSummaryResponse(request_id=request_id,top5= None, least= 0,
                                                              median= 0,timestamp=timestamp)
        word_service = WordService()
        word_service._word_storage._word_freq = dict()
        response = await word_service.get_stats_summary(request_id)
        assert response.top5 == expected_empty_summary.top5
        assert response.least == expected_empty_summary.least
        assert response.median == expected_empty_summary.median

    async def test_word_service_with_five_words(self):
        words = ["ball","eggs","pool","dart","table"]
        request_id = str(uuid.uuid4())
        timestamp = str(datetime.now(timezone.utc))
        expected_summary = WordProcessorSummaryResponse(request_id=request_id,
                                                        top5={'ball': 1, 'eggs': 1, 'pool': 1, 'dart': 1, 'table': 1},
                                                        least= 1,median= 1,timestamp=timestamp)
        word_service = WordService()
        word_service._word_storage._word_freq = dict()
        await word_service.add_words(words,request_id)
        response = await word_service.get_stats_summary(request_id)
        assert response.least == expected_summary.least
        assert response.top5 == expected_summary.top5
        assert response.median == expected_summary.median

    async def test_word_service_with_repeating_words(self):
        words = ["ball","eggs","pool","dart","ball","ball","table","eggs","pool","mouse","ball","eggs","table","mouse"]
        request_id = str(uuid.uuid4())
        timestamp = str(datetime.now(timezone.utc))
        expected_summary = WordProcessorSummaryResponse(request_id=request_id,
                                                        top5= {'ball': 4, 'eggs': 3, 'pool': 2, 'table': 2, 'mouse': 2},
                                                        least= 1, median= 2,timestamp=timestamp)
        word_service = WordService()
        word_service._word_storage._word_freq = dict()
        await word_service.add_words(words,request_id)
        response = await word_service.get_stats_summary(request_id)
        assert response == expected_summary

    async def test_word_service_with_one_word(self):
        words = ["ball", "ball", "ball", "ball"]
        request_id = str(uuid.uuid4())
        timestamp = str(datetime.now(timezone.utc))
        expected_summary = WordProcessorSummaryResponse(request_id=request_id,top5={'ball': 4},
                                                              least= 4, median=4,timestamp=timestamp)
        word_service = WordService()
        word_service._word_storage._word_freq = dict()
        await word_service.add_words(words, request_id)
        response = await word_service.get_stats_summary(request_id)
        assert response.top5 == expected_summary.top5
        assert response.least == expected_summary.least
        assert response.median == expected_summary.median

