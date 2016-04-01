# Gradle Wrapper
>Gradle Wrapper是更好的启动Gradle构建的方式。

Gradle Wrapper(后面称为"wrapper")是更好的启动Gradle构建的方式。这个wrapper在Windows上是一个batch脚本，在其他操作系统上是一个shell脚本。当你通过wrapper启动Gradle时，Gradle会自动被下载并用于构建。

应当把wrapper提交到版本控制系统。通过将wrapper跟项目一起发布，所有基于它工作的人事先不必安装Gradle。另一个好处是，可以保证构建者使用指定的Gradle版本进行构建。当然，这对持续构建服务器来说也非常有用，因为它不需要进行任何配置。

通过运行wrapper task来安装wrapper。(这个task一直存在，即使用你没有在构建中加入)。通过--gradle-version来指定Gradle版本。通过--gradle-distribution-url指定下载Gradle的URL。如果没有指定这个URL，将下载执行wrapper task时的Gradle版本。所以当你使用Gradle 2.4运行wrapper task时，wrapper会默认配置为Gradle 2.4。

下载Gradle时出现这个问题：
`Exception in thread "main" java.lang.RuntimeException: java.net.ConnectException: Connection timed out: connect`

需要手动下载Gradle版本，这次react-native装的是gradle-2.2-all.zip的版本。

象maven一样解压配置gradle的环境变量，GRADLE_HOME配置根路径，bin目录配置进入path。

另外在gradle-wrapper.properties文件中，指定本地gradle-2.2-all.zip的路径。
`distributionUrl=file\:/d:/gradle-2.2.1-all.zip` or `distributionUrl=file\:/Users/liangck/jplugin/gradle-2.2-all.zip`
