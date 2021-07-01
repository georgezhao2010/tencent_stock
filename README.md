# Tencent Stocks

腾讯股票的Home Assistant插件，可以将每一只股票转为一个Sensor，State为当前价格。

同时可以将该只股票的其它信息显示为属性


![A](https://user-images.githubusercontent.com/27534713/124057266-b8a99c80-da59-11eb-86e7-3627b08ab12f.png)


# 安装

使用HACS自定义存储库安装或者从[Latest Release](https://github.com/georgezhao2010/tencent_stock/releases/latest)下载最新的Release，并将其中的`custom_components/tencent_stock`目录下所有文件放到你的Home Assistant的`<Home Assistant Config Folder>/custom_components/tencent_stock`中，然后重新启动Home Assistant。

# 配置

在configuration.yaml中添加以下内容
```
tencent_stock:
  stocks:
    sh: ['000001','600029','600519']
    sz: ['399001','399006']
```
其中sh代表上交所的股票配置，sz代表深交所的股票配置。

交易时间默认为每天9:15-11:30,13:00-15:00两个时间段，你也可以在配置文件中自定义交易时间段
```
tencent_stock:
  time_slices:
    - begin_time: '9:15'
      end_time: '11:30'
    - begin_time: '13:00'
      end_time: '15:00'
  stocks:
    sh: ['000001','600029','600519']
    sz: ['399001','399006']
```

# 数据更新

在交易日的交易时间段内每10秒更新一次数据，在非交易时间段内每10小时更新一次数据，周六日默认不属于交易日。
