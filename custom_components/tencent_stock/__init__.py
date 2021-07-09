import logging
import async_timeout
import requests
import datetime
import asyncio
import re
from datetime import timedelta
from homeassistant.helpers import discovery
from homeassistant.core import HomeAssistant
from.const import (DOMAIN,
                   REPOS_API_URL,
                   CONF_EXCHANGE,
                   CONF_STOCK,
                   MIN_UPDATE_INTERVAL,
                   MAX_UPDATE_INTERVAL,
                   TIME_SLICES)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, hass_config: dict):
    config = hass_config[DOMAIN]
    coordinator = StockCorrdinator(hass, config)
    hass.data[DOMAIN] = coordinator
    await coordinator.async_refresh()
    hass.async_create_task(discovery.async_load_platform(
        hass, "sensor", DOMAIN, config, hass_config))

    return True

UPDATE_INTERVAL = timedelta(seconds=MIN_UPDATE_INTERVAL)


class StockCorrdinator(DataUpdateCoordinator):
    _tencent_data_format = ['stock', 'unused', 'name', '股票代码', '当前价格', '昨收', '今开', '成交量(手)', '外盘', '内盘',
                            '买一', '买一量(手)', '买二', '买二量(手)', '买三', '买三量(手)', '买四', '买四量(手)', '买五',
                            '买五量(手)', '卖一', '卖一量(手)', '卖二', '卖二量(手)', '卖三', '卖三量(手)', '卖四',
                            '卖四量(手)', '卖五', '卖五量(手)', 'unknown1', 'datetime', '涨跌', '涨跌(%)', '最高', '最低',
                            '价格/成交量(手)/成交额', '成交量(手)', '成交额(万)', '换手率', '市盈率', 'unknown2', '最高1', '最低1', '振幅',
                            '流通市值', '总市值', '市净率', '涨停价', '跌停价', '量比', '委差', '均价', '市盈(动)', '市盈(静)']
    _tencent_data_patten = re.compile(r'v_([-/\.\w]*)="([\w]*)' + (r'~([-/\.\w]*)' * (len(_tencent_data_format) - 2)))

    def __init__(self, hass, config):
        self._hass = hass
        self._quest_url = REPOS_API_URL
        if config is not None and "time_slices" in config:
            self._time_slice = config["time_slices"]
        else:
            self._time_slice = TIME_SLICES
        _LOGGER.debug(self._time_slice)
        self._count = MAX_UPDATE_INTERVAL
        for exchange, stocks in config["stocks"].items():
            for stock in stocks:
                self._quest_url = self._quest_url + exchange + stock + ","

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    def format_response_data(self, res_data):
        res_data = res_data.replace(" ", "")
        data = "".join(res_data)
        data = self._tencent_data_patten.finditer(data)
        result_list = {}
        for item in data:
            assert len(self._tencent_data_format) == len(item.groups())
            single = dict(zip(self._tencent_data_format, item.groups()))
            result_list[single["stock"]] = single
        return result_list

    def in_time_slice(self, ):
        now_time = datetime.datetime.now()
        if now_time.weekday() > 4:
            return False
        for single_slice in self._time_slice:
            begin_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + single_slice["begin_time"],
                                                    '%Y-%m-%d%H:%M') - datetime.timedelta(minutes=2)
            end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + single_slice["end_time"],
                                                  '%Y-%m-%d%H:%M') + datetime.timedelta(minutes=2)
            if begin_time <= now_time <= end_time:
                return True
        return False

    async def _async_update_data(self):
        data = self.data
        if self.in_time_slice() or self._count >= MAX_UPDATE_INTERVAL:
            try:
                async with async_timeout.timeout(3):
                    r = await self._hass.async_add_executor_job(
                        requests.get,
                        self._quest_url
                    )
                    if r.status_code == 200:
                        self._count = 0
                        data = self.format_response_data(r.text)
                        _LOGGER.debug(f"Successful to update stock data {data}")
            except asyncio.TimeoutError:
                _LOGGER.debug("Data update timed out")
        else:
            self._count = self._count + MIN_UPDATE_INTERVAL
            _LOGGER.debug(f"Now time not in slice, count = {self._count}")
        return data
