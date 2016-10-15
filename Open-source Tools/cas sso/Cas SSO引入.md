# CAS
> Yale大学发起的一个开源的单点登录(Single Sign On, SSO)框架。

**以下以 cas 4.0.x 版本为例（因为这个版本应用比较广泛，文档比较多）。**

[cas server下载地址](https://www.apereo.org/projects/cas/download-cas)： `https://www.apereo.org/projects/cas/download-cas`

#　关闭　CAS-Server 的HTTPS验证

## cas-server\WEB-INF\deployerConfigContext.xml 文件

```xml
<!-- Required for proxy ticket mechanism. -->
    <bean id="proxyAuthenticationHandler"
class="org.jasig.cas.authentication.handler.support.HttpBasedServiceCredentialsAuthenticationHandler"
          p:httpClient-ref="httpClient" />

<!--
增加参数p:requireSecure="false"，是否需要安全验证，即HTTPS，false为不采用。修改后为：
 -->

  <bean id="proxyAuthenticationHandler"
class="org.jasig.cas.authentication.handler.support.HttpBasedServiceCredentialsAuthenticationHandler"
          p:httpClient-ref="httpClient" p:requireSecure="false" />
```

##  cas-server\WEB-INF\spring-configuration\ticketGrantingTicketCookieGenerator.xml 文件

```xml
<bean id="ticketGrantingTicketCookieGenerator" class="org.jasig.cas.web.support.CookieRetrievingCookieGenerator"
        p:cookieSecure="true"
        p:cookieMaxAge="-1"
        p:cookieName="CASTGC"
        p:cookiePath="/cas" />

<!--
  修改  p:cookieSecure="true" 为 p:cookieSecure="false"
  即不开启https验证
 -->

```

## cas-server\WEB-INF\spring-configuration\warnCookieGenerator.xml 文件

```xml
<bean id="warnCookieGenerator" class="org.jasig.cas.web.support.CookieRetrievingCookieGenerator"
        p:cookieSecure="true"
        p:cookieMaxAge="-1"
        p:cookieName="CASPRIVACY"
        p:cookiePath="/cas" />

<!--
  修改  p:cookieSecure="true" 为 p:cookieSecure="false"
  即不开启https验证
 -->        

```

# 数据库身份验证
通过配置，从数据验证用户登录信息

验证配置都是在 `deployerConfigContext.xml`配置文件中

## 默认验证

```xml
<bean id="primaryAuthenticationHandler"
          class="org.jasig.cas.authentication.AcceptUsersAuthenticationHandler">
        <property name="users">
            <map>
                <entry key="casuser" value="Mellon"/>
            </map>
        </property>
    </bean>
```
即用户名为 `casuser`, 密码为 `Mellon`。


## 配置通过数据验证

注释掉 `<bean  class="org.jasig.cas.authentication.handler.support.SimpleTestUsernamePasswordAuthenticationHandler" />  
`，或上图的
```xml
<bean id="primaryAuthenticationHandler"
          class="org.jasig.cas.authentication.AcceptUsersAuthenticationHandler">
        <property name="users">
            <map>
                <entry key="casuser" value="Mellon"/>
            </map>
        </property>
    </bean>
```

 然后添加
```xml
    <!--
      也就是将上面的 SimpleTestUsernamePasswordAuthenticationHandler 或 AcceptUsersAuthenticationHandler
      修改为 QueryDatabaseAuthenticationHandler
    -->
    <bean id="primaryAuthenticationHandler" class="org.jasig.cas.adaptors.jdbc.QueryDatabaseAuthenticationHandler">
        <property name="dataSource" ref="dataSource"></property>
        <property name="sql" value="select password from v_password where login_name = ? "></property>
    </bean>

    <!-- 配置 QueryDatabaseAuthenticationHandler 的数据源信息 -->
    <bean id="dataSource" class="org.apache.commons.dbcp.BasicDataSource">
        <property name="driverClassName" value="com.mysql.jdbc.Driver" />
        <property name="url" value="jdbc:mysql://127.0.0.1:5688/biz?useUnicode=true&amp;characterEncoding=utf-8&amp;zeroDateTimeBehavior=convertToNull" />
        <property name="username" value="root" />
        <property name="password" value="root123456" />
    </bean>
```

如此，OK。在登录时输入对应表中的对应用户名，密码就可以了。

当然，以上只是默认密码为原始的明文密码。如果有自己的加密规则，可以通过自定义 `PasswordEncoder`来实现密码的加密对比。

如：
```java
import org.jasig.cas.authentication.handler.PasswordEncoder;

public class MyPasswordEncoder implements PasswordEncoder {

    public static final String MD5PREX = "TEST_SALT";


    @Override
    public String encode(final String password) {

        final String encryptedPwd = MD5.toMD5(MD5PREX + password);

        return encryptedPwd;
    }
}

```

然后修改 `deployerConfigContext.xml` 文件
```xml
<!-- 加入 YzfPasswordEncoder -->
<bean id="myPasswordEncoder" class="com.liangck.cas.MyPasswordEncoder"/>

<!-- 修改 primaryAuthenticationHandler（QueryDatabaseAuthenticationHandler），加入 PasswordEncoder配置 -->
<bean id="primaryAuthenticationHandler" class="org.jasig.cas.adaptors.jdbc.QueryDatabaseAuthenticationHandler">
        <property name="dataSource" ref="dataSource"></property>
        <property name="sql" value="select password from v_password where login_name = ? "></property>
        <property name="passwordEncoder" ref="myPasswordEncoder"></property>
    </bean>

```

如此，就可以根据现有系统的加密方式来验证用户信息了。

## 登录后返回更多用户信息
现实系统中有很多这样的需求：登录后返回更多的用户信息（如用户名等），存在当前session或内存中，以便随时可以使用。

可以通过如下配置来实现：

首先打开 `deployerConfigContext.xml`：

```xml
  <!--
       | Resolves a principal from a credential using an attribute repository that is configured to resolve
       | against a deployer-specific store (e.g. LDAP).
       -->
    <bean id="primaryPrincipalResolver"
          class="org.jasig.cas.authentication.principal.PersonDirectoryPrincipalResolver" >
        <property name="attributeRepository" ref="attributeRepository" />
    </bean>

    <!--
    Bean that defines the attributes that a service may return.  This example uses the Stub/Mock version.  A real implementation
    may go against a database or LDAP server.  The id should remain "attributeRepository" though.
    +-->
    <bean id="attributeRepository" class="org.jasig.services.persondir.support.StubPersonAttributeDao"
          p:backingMap-ref="attrRepoBackingMap" />

    <util:map id="attrRepoBackingMap">
        <entry key="uid" value="uid" />
        <entry key="eduPersonAffiliation" value="eduPersonAffiliation" />
        <entry key="groupMembership" value="groupMembership" />
    </util:map>
```

可以看到（可以查看PersonDirectoryPrincipalResolver源码），cas 通过 `org.jasig.cas.authentication.principal.PersonDirectoryPrincipalResolver`来解析属性`attributeRepository`中的map信息，来存储进`Principal`中。

### 定义自己的 `attributeRepository`:
```xml

<!-- 使用 SingleRowJdbcPersonAttributeDao 从指定数据源，通过指定语句，返回指定的信息-->
<bean id="ssoAttributeRepository" class="org.jasig.services.persondir.support.jdbc.SingleRowJdbcPersonAttributeDao">
        <constructor-arg index="0" ref="dataSource"></constructor-arg>
        <constructor-arg index="1" value="select * from v_user where login_name = ?"></constructor-arg>
        <!-- 组装sql用的查询条件属性  -->
        <property name="queryAttributeMapping" ref="queryAttributeMapping"/>
        <property name="resultAttributeMapping" ref="resultAttributeMapping"/>
    </bean>
    <util:map id="queryAttributeMapping">
        <!-- key必须是uername而且是小写否则会导致取不到用户的其它信息，value对应数据库用户名字段,系统会自己匹配 -->
        <entry key="username" value="login_name" />
    </util:map>
    <util:map id="resultAttributeMapping">
        <!-- key为对应的数据库字段名称，value为提供给客户端获取的属性名字，系统会自动填充值  -->
        <entry key="login_name" value="username"></entry>
        <entry key="id" value="id"></entry>
        <entry key="cls_name" value="domain"></entry>
        <entry key="org_id" value="orgId"></entry>
        <entry key="status" value="status"></entry>

    </util:map>
```

### 修改 `casServiceValidationSuccess.jsp` 文件
  CASServer要将额外的信息传递至Client端，还需要修改完成信息组装的文件WEB-INF/view/jsp/protocol/2.0/casServiceValidationSuccess.jsp。casServiceValidationSuccess.jsp负责组装包含用户信息的XML，因此修改部分是将需要传递的额外信息加入到它最终生成的XML文件之中。具体修改如下：

  ```jsp
  <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationSuccess>
        <cas:user>${fn:escapeXml(assertion.primaryAuthentication.principal.id)}</cas:user>

　　　　<!-- 这段 -- >
        <c:if test="${fn:length(assertion.chainedAuthentications[fn:length(assertion.chainedAuthentications)-1].principal.attributes) > 0}">
            <cas:attributes>
                <c:forEach var="attr" items="${assertion.chainedAuthentications[fn:length(assertion.chainedAuthentications)-1].principal.attributes}">
                    <cas:${fn:escapeXml(attr.key)}>${fn:escapeXml(attr.value)}</cas:${fn:escapeXml(attr.key)}>
                </c:forEach>
            </cas:attributes>
        </c:if>
        <!-- 这段 end-- >


        <c:if test="${not empty pgtIou}">
                <cas:proxyGrantingTicket>${pgtIou}</cas:proxyGrantingTicket>
        </c:if>
        <c:if test="${fn:length(assertion.chainedAuthentications) > 1}">
          <cas:proxies>
            <c:forEach var="proxy" items="${assertion.chainedAuthentications}" varStatus="loopStatus" begin="0" end="${fn:length(assertion.chainedAuthentications)-2}" step="1">
                 <cas:proxy>${fn:escapeXml(proxy.principal.id)}</cas:proxy>
            </c:forEach>
          </cas:proxies>
        </c:if>
    </cas:authenticationSuccess>
</cas:serviceResponse>
  ```

### 客户端获取

在客户端通过如下方式获取，以jsp文件为例：
```jsp
<!DOCTYPE html">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>返回值测试</title>
</head>
<body>

<%
   request.setCharacterEncoding("UTF-8");
   AttributePrincipal principal = (AttributePrincipal) request.getUserPrincipal();
   Map attributes = principal.getAttributes();
   String id=(String)attributes.get("id");
   String loginName = (String)attributes.get("loginName");
   String orgId = (String)attributes.get("orgId");
   String status = (String)attributes.get("status");
   String clsName = (String)attributes.get("clsName");
   %>
   <div>登录成功-返回值测试</div>
   <ul>
       <li>用户ID：<%= id%></li>
       <li>loginName: <%= loginName%></li>
       <li>clsName：<%= clsName%></li>
       <li>orgId：<%= orgId%></li>
       <li>status: <%= status%></li>

   </ul>

   <a href="http://localhost:8080/cas/logout?service=http://localhost:8088/examples">登出</a>
</body>
</html>
```

# 客户端配置

## 引入相关jar包

客户端代码地址：`git@github.com:apereo/java-cas-client.git`，git clone到本地，切换到指定的发布标签（如 3.3.3-RELEASE）， `mvn clean install` 编译得到 java-cas-client-core-3.3.3.jar 包，在项目中引入该jar包，还有日志依赖包：

* slf4j-api-1.7.2.jar
* slf4j-log4j12-1.7.2.jar
* log4j-1.2.17.jar

## 修改 web.xml 配置

web.xml 中加入以下配置：

注：client jar 包版本不对，可能会报该配置错误，如`CASSingle Sign OutFilter param casServerUrlPrefix can't be null`之类。

```xml
<!-- ========================单点登录开始 ======================== -->
    <!--用于单点退出，该过滤器用于实现单点登出功能，可选配置 -->
    <listener>
        <listener-class>org.jasig.cas.client.session.SingleSignOutHttpSessionListener</listener-class>
    </listener>
    <!--该过滤器用于实现单点登出功能，可选配置。 -->
    <filter>
        <filter-name>CASSingle Sign OutFilter</filter-name>
        <filter-class>org.jasig.cas.client.session.SingleSignOutFilter</filter-class>
    </filter>
    <filter-mapping>
        <filter-name>CASSingle Sign OutFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>
    <filter>
        <filter-name>CASFilter</filter-name>
        <filter-class>org.jasig.cas.client.authentication.AuthenticationFilter</filter-class>
        <init-param>
            <param-name>casServerLoginUrl</param-name>
            <param-value>http://localhost:8080/cas-server/login</param-value>
        </init-param>
        <init-param>
            <param-name>serverName</param-name>
            <param-value>http://localhost:8088</param-value>
        </init-param>
    </filter>
    <filter-mapping>
        <filter-name>CASFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>
    <!--该过滤器负责对Ticket的校验工作，必须启用它 -->
    <filter>
        <filter-name>CASValidationFilter</filter-name>
        <filter-class>
            org.jasig.cas.client.validation.Cas20ProxyReceivingTicketValidationFilter
        </filter-class>
        <init-param>
            <param-name>casServerUrlPrefix</param-name>
            <param-value>http://localhost:8080/cas-server</param-value>
        </init-param>
        <init-param>
            <param-name>serverName</param-name>
            <param-value>http://localhost:8088</param-value>
        </init-param>
    </filter>
    <filter-mapping>
        <filter-name>CASValidationFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>
    <!-- 该过滤器负责实现HttpServletRequest请求的包裹， 比如允许开发者通过HttpServletRequest的getRemoteUser()方法获得SSO登录用户的登录名，可选配置。 -->
    <filter>
        <filter-name>CASHttpServletRequest WrapperFilter</filter-name>
        <filter-class>
            org.jasig.cas.client.util.HttpServletRequestWrapperFilter
        </filter-class>
    </filter>
    <filter-mapping>
        <filter-name>CASHttpServletRequest WrapperFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>
    <!-- 该过滤器使得开发者可以通过org.jasig.cas.client.util.AssertionHolder来获取用户的登录名。 比如AssertionHolder.getAssertion().getPrincipal().getName()。 -->
    <filter>
        <filter-name>CASAssertion Thread LocalFilter</filter-name>
        <filter-class>org.jasig.cas.client.util.AssertionThreadLocalFilter</filter-class>
    </filter>
    <filter-mapping>
        <filter-name>CASAssertion Thread LocalFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>
    <!-- ========================单点登录结束 ======================== -->
```

以上，启动客户端应用后，会重定向到cas-server 的登录页面。登陆后会返回客户端应用。
