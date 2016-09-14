# @RequestBody

从http body中获取参数不需要key，支持`application/json`的媒体类型。

如Controller：
```java
@RequestMapping(value = "/testRequesetBodyParam", method = {RequestMethod.GET, RequestMethod.POST})
@ApiOperation(value = "测试RequestBody注解")
public AjaxResult<String> testRequesetBodyParam(@RequestBody @ApiParam(value = "测试RequestBody注解", required = true) String xml) {
}
```

python 调用如下:
```python
#!/usr/bin/python
# __encoding:utf-8__
#

import urllib
import urllib2

"""
发送表单数据
"""

url = 'http://127.0.0.1:8080/testRequesetBodyParam'

# value
values = """
<?xml version="1.0" encoding="UTF-8" ?>
<ExchangeData>
    <GUID>F14F524C-6580-42de-9EEF-998B3FF2D81F</GUID>
    <CompanyInfo>
        <Account>zengzhaojia</Account>
    </CompanyInfo>
    <InvoiceEnterprise>
        <EnterpriseInfo>
            <TaxCode>320102783816697</TaxCode>
        </EnterpriseInfo>
        <EnterpriseInfo>
            <TaxCode>91320104302767442H</TaxCode>
        </EnterpriseInfo>
        <EnterpriseInfo>
            <TaxCode>320114302599151</TaxCode>
        </EnterpriseInfo>
    </InvoiceEnterprise>
</ExchangeData>
""";
# data = {'data': values}

# 需设置 Content-Type
headers = {'Content-Type': 'application/json'}
# value直接放入http body中
req = urllib2.Request(url, values, headers)
response = urllib2.urlopen(req).read()
print response
```
