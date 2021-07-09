import logging
from .const import DOMAIN
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.update_coordinator import CoordinatorEntity


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    sensors = []
    coordinator = hass.data[DOMAIN]
    for exchange, stocks in discovery_info["stocks"].items():
        for stock in stocks:
            sensors.append(StockSensor(coordinator, exchange + stock))
    async_add_devices(sensors, True)


class StockSensor(CoordinatorEntity):
    def __init__(self, coordinator, stock):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._stock = stock
        self._unique_id = f"{DOMAIN}.stock_{stock}"
        self.entity_id = self._unique_id
        self._is_index = (stock[0:2] == "sh" and stock[2:5] == "000") or (stock[0:2] == "sz" and stock[2:5] == "399")

    def get_value(self, key):
        if self._coordinator.data is not None and self._coordinator.data.get(self._stock) is not None:
            return self._coordinator.data.get(self._stock).get(key)
        else:
            return STATE_UNKNOWN

    @staticmethod
    def sign(str_val):
        if str_val != STATE_UNKNOWN and float(str_val) != 0 and str_val[0:1] != "-":
            return "+" + str_val
        return str_val

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return f"{self.get_value('name')}({self._stock}) [{self.sign(self.get_value('涨跌'))}" \
               f"({self.sign(self.get_value('涨跌(%)'))}%)]"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        _state = self.get_value('当前价格')
        if _state != STATE_UNKNOWN:
            return float(self.get_value('当前价格'))
        else:
            return _state

    @property
    def device_state_attributes(self) -> dict:
        ret = {
            "股票代码": self.get_value("股票代码"),
            "当前价格": self.get_value("当前价格"),
            "昨收": self.get_value("昨收"),
            "今开": self.get_value("今开"),
            "成交量": self.get_value("成交量(手)"),
            "外盘": self.get_value("外盘"),
            "内盘": self.get_value("内盘"),
            "涨跌": self.sign(self.get_value("涨跌")),
            "涨跌幅": self.sign(self.get_value("涨跌(%)")) + "%",
            "最高": self.get_value("最高"),
            "最低": self.get_value("最低"),
            "成交额": self.get_value("成交额(万)"),
            "振幅": self.get_value("振幅") + "%",
        }

        if not self._is_index:
            ret.update({
                "卖五(" + self.get_value("卖五") + ")": self.get_value("卖五量(手)"),
                "卖四(" + self.get_value("卖四") + ")": self.get_value("卖四量(手)"),
                "卖三(" + self.get_value("卖三") + ")": self.get_value("卖三量(手)"),
                "卖二(" + self.get_value("卖二") + ")": self.get_value("卖二量(手)"),
                "卖一(" + self.get_value("卖一") + ")": self.get_value("卖一量(手)"),
                "买一(" + self.get_value("买一") + ")": self.get_value("买一量(手)"),
                "买二(" + self.get_value("买二") + ")": self.get_value("买二量(手)"),
                "买三(" + self.get_value("买三") + ")": self.get_value("买三量(手)"),
                "买四(" + self.get_value("买四") + ")": self.get_value("买四量(手)"),
                "买五(" + self.get_value("买五") + ")": self.get_value("买五量(手)"),
                "换手率": self.get_value("换手率") + "%",
                "市盈率": self.get_value("市盈率"),
                "流通市值": self.get_value("流通市值"),
                "总市值": self.get_value("总市值"),
                "市净率": self.get_value("市净率"),
                "量比": self.get_value("量比"),
                "均价": self.get_value("均价"),
                "涨停价": self.get_value("涨停价"),
                "跌停价": self.get_value("跌停价"),
                "委差": self.get_value("委差"),
                "市盈(动)": self.get_value("市盈(动)"),
                "市盈(静)": self.get_value("市盈(静)")
            })
        return ret

    @property
    def unit_of_measurement(self):
        if self._is_index:
            return "点"
        else:
            return "元"

    @property
    def icon(self):
        return "hass:pulse"
