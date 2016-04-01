##### distutils
> distutils 是python标准库的一部分，这个库的目的是为开发者提供一种方便的打包方式，同时为使用者提供方便的安装方式。  
我们经常使用的setup.py就是基于distutils实现的，然后通过setup.py就可以进行打包或者安装了。

一个煎蛋的例子，找一个目录创建三个文件 foo.py、bar.py 和 setup.py，其中setup.py的内容如下：  

    from distutils.core import setup
    setup(
      name='fooBar',
      version='1.0',
      author='Will',
      author.email='willber@sh.com',
      url='http://cnblogs.com/wilber2013',
      py_modules=['foo', 'bar'],
    )
然后在该目录运行`python setup.py sdist`，会生成一个`fooBar-1.0.zip`包。  使用者就可以解压缩这个包然后执行`python setup.py install`进行安装，然后就可以使用foo、bar这个两个模块了。

##### setuptools和distribute
setuptools是对disutils的增强，尤其是引入了包依赖管理。我们可以通过`ez_setup.py`来安装`setuptools`。   ／
至于distribute，他是setuptools的一个分支版本。分支的原因是有一部分开发者认为setuptools开发太慢。但现在，distribute又合并到setuptools中，所以可以认为它们是同一个东西。   

前面看到`setup.py`可以创建一个压缩包，而setuptools使用了一种新的文件格式(.egg)，可以为Python包创建egg文件。setuptools可以识别`.egg`文件。setuptools可以识别`.egg`文件，并解析，安装它。

**easy_install**
当安装好setuptools/distribute之后，我们就可以直接使用`easy_install`这个工具了：  
1. 从[PyPI](https://pypi.python.org/pypi)上安装一个包：当使用`easy_install package`命令后，easy_install就可以自动从PyPI上下载相关的包。并完成安装，升级。
2. 下载一个包安装：通过`easy_install package.tgz` 可以安装一个已经下载的包。
3. 安装egg文件：通过`easy_install package.egg`可以安装一个egg格式的文件。

通过`easy_install --help` 可以获取该命令的相关帮助提示。

![](tupian.png)

##### 以上，setuptools/distribute 和 easy_install之间的关系：
* setuptools/distribute 都扩展了distutils，提供了更多的功能
* easy_install 是基于setuptools/distribute 的一个工具，方便了包的安装和升级

##### pip
> pip是目前最流行的Python包管理工具，它被当作easy_install的替代品，但是仍有大量的功能建立在setuptools之上。  

easy_install有很多不足：安装事务是非原子操作，只支持svn，没有提供卸载命令，安装一系列包时需要写脚本。  
pip的使用非常简单：  
* 安装：`pip install SomePackage`  
* 卸载：`pip uninstall SomePackage`
* 查看帮助文档：pip --help
* 查看已安装的软件包：pip list
* 查看可升级的软件包：pip list --outdated
* 升级软件包：pip install --upgrade SomePackage
* 查看软件包安装了哪些文件及路径等信息 pip show --files SomePackage
* 安装软件包的指定版本号：
  1. pip install SomePackage    #last version
  2. pip install SomePackage==1.0.4 #specific version
  3. pip install 'SomePackage>=1.0.4' #minimum version
* 根据依赖文件安装软件包：
  1. pip freeze > requirements.txt #使用pip导出依赖文件列表
  2. pip install -r requirements.txt #根据依赖文件列表，自动安装对应的软件包
