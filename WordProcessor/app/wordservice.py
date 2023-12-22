import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict

from WordProcessor.app.objects import WordProcessorSummaryResponse

logger = logging.getLogger(__name__)


class _WordStorage:
    _word_freq: Dict[str, int] = dict()

    dict_add_lock = asyncio.Lock()

    async def add_word(self, word: str) -> None:
        async with self.dict_add_lock:
            self._word_freq.setdefault(word, 0)
            current_counter=  self._word_freq[word]
            self._word_freq[word] = current_counter+1 if current_counter >= 0 else 1

    def get_freq(self,word) -> int:
        return self._word_freq[word]

    def get_min_freq_value(self) -> int:
        return min(self._word_freq.values())

    def get_median_freq_value(self) -> int:
        frequency_list = sorted(self._word_freq.values())
        return frequency_list[int(len(frequency_list)/2)]

    def get_most_occurring_words(self):
        frequency_list = sorted(self._word_freq.items(), key=lambda x: x[1], reverse=True)
        return frequency_list[:5]


class WordService:
    _word_storage = _WordStorage()

    async def add_words(self, words: List[str], request_id: str) -> None:
        logger.info(f"adding words from request: {request_id}")
        for word in words:
            await self._word_storage.add_word(word)
            logger.debug(f'word is {word} count is {self._word_storage.get_freq(word)} . request: {request_id}')
        logger.info(f"finished adding words from request: {request_id}")

    async def get_stats_summary(self, request_id: str) -> WordProcessorSummaryResponse:
        timestamp = str(datetime.now(timezone.utc))
        try:
            least_freq = await self._get_least_frequency()
            median_freq = await self._get_median_frequency()
            top_five = await self._get_top_five()
            summary = WordProcessorSummaryResponse(request_id=request_id, top5 = top_five,
                                                   least=least_freq, median=median_freq, timestamp=timestamp)
            return summary
        except ValueError as e:
            logger.debug(e)
            summary = await self._get_empty_summary_and_log_warning(request_id, f"no data inserted yet,"
                                                                                f" problem getting min value."
                                                                                f" request {request_id}",timestamp)
            return summary
        except IndexError as e:
            logger.debug(e)
            summary = await self._get_empty_summary_and_log_warning(request_id, f'no data inserted yet,'
                                                                                f' problem getting median value.'
                                                                                f' request {request_id}',timestamp)
            return summary
        except Exception as e:
            logger.error(f'request - {request_id} an unexpected error occured {e}')
            raise e
            # return self._get_empty_summary_and_log_warning(request_id, f"unexpected error for request {request_id}")

    async def _get_empty_summary_and_log_warning(self, request_id: str,log_error: str,timestamp: str):
        logger.warning(log_error)
        summary = WordProcessorSummaryResponse(request_id=request_id, top5=None,
                                               least=0, median=0,timestamp=timestamp)
        return summary

    async def _get_least_frequency(self):
        return self._word_storage.get_min_freq_value()

    async def _get_median_frequency(self):
        return self._word_storage.get_median_freq_value()

    async def _get_top_five(self):
        top_five=dict()
        for word_item in self._word_storage.get_most_occurring_words():
            top_five[word_item[0]] = word_item[1]
        return top_five



