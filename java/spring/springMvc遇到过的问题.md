### spring mvc接收自定义对象
>官方的[spring-mvc-showcase](https://github.com/spring-projects/spring-mvc-showcase/blob/master/src%2Ftest%2Fjava%2Forg%2Fspringframework%2Fsamples%2Fmvc%2Fconvert%2FConvertControllerTests.java)可以看到。

在在项目中有个修改订单的场景，可以修改订单的订单商品列表，即修改已购买的商品的价格，数量，所以需要将修改后的订单商品列表(orderGoodsList)传到后台Controller，试过多次，最后才成功，现记录一下。
后台的自定义对象需要一个包装对象来接收数据。
1. 订单商品类

        public class WholesaleOrderGoods implements Serializable {
          ...
        }
2. 订单商品列表的包装类

        public class GoodsListWrapper {

            List<WholesaleOrderGoods> orderGoodsList;

            public GoodsListWrapper() {
            }

            public List<WholesaleOrderGoods> getOrderGoodsList() {
                return orderGoodsList;
            }

            public void setOrderGoodsList(List<WholesaleOrderGoods> orderGoodsList) {
                this.orderGoodsList = orderGoodsList;
            }
        }
3. Controller

            @RequestMapping("/doModifyOrder")
            @ResponseBody
            public BaseResponse doModifyOrder(@RequestParam("orderId") Long orderId, @RequestParam("freightPrice") BigDecimal freightPrice, GoodsListWrapper goodsListWrapper, HttpServletRequest request)throws KBossException{
                List<WholesaleOrderGoods> orderGoodses = goodsListWrapper.getOrderGoodsList();
                // 参数检查
                // todo...
                // 修改订单
                // todo...
            }
4. 前台js代码

        var data = "";
        //遍历所有订单商品项,封装json数据
        $("tr.order-goods-item").each(function(idx){
            var orderGoodsId = $(this).find("input.order-goods-id").val();
            var orderGoodsNum = $(this).find("input.goods-num").val();
            var orderGoodsPrice = $(this).find("input.goods-price").val();
            data+="&orderGoodsList["+idx+"].orderGoodsId="+orderGoodsId+"&orderGoodsList["+idx+"].goodsNum="+orderGoodsNum+"&orderGoodsList["+idx+"].wholesalePrice="+orderGoodsPrice;
        });
        $.ajax({
            url: 'doModifyOrder.htm',
            dataType: 'json',
            type: 'post',
            cache: false,
            data: data,
            success: function(data){
              // todo...
            },
            error: function(jqXHR, textStatus, errorMsg){
              // todo...
            }
        });
即最后封装的数据格式是：`orderGoodsList[0].orderGoodsId=''&orderGoodsList[0].orderGoodsNum=''&orderGoodsList[0].orderGoodsPrice=''&orderGoodsList[1].orderGoodsId=''&orderGoodsList[1].orderGoodsNum=''&orderGoodsList[1].orderGoodsPrice=''`
直接用list接收竟然不可以。。555。反正这次是没发现有什么更好的方式
